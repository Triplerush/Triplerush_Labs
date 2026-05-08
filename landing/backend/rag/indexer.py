"""
indexer.py — RAG Index Builder

Loads portfolio nodes (JSON), generates embeddings with Gemini
gemini-embedding-001 via google-genai, and builds an in-memory
cosine-similarity index using NumPy.

No FAISS, no sentence-transformers, no PyTorch — pure google-genai + NumPy.
The dataset is small, so a brute-force NumPy search is instant.
"""

import json
import os
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field

import numpy as np
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# ─── Embedding config ────────────────────────────────────────
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 256  # reduced dimensionality (256 is enough for ~15 chunks)


@dataclass
class Chunk:
    """A chunk of text with metadata for RAG retrieval."""
    text: str
    source: str  # node type, for example "project" or "experience-bundle"
    section: str  # header or node name
    metadata: dict = field(default_factory=dict)


@dataclass
class Node:
    """Normalized portfolio node used by constellation matching."""
    id: str
    type: str
    name: str
    category: str
    is_central: bool
    data: dict = field(default_factory=dict)


@dataclass
class RAGIndex:
    """Container for the embedding matrix and associated chunks."""
    embeddings: np.ndarray  # shape: (n_chunks, EMBEDDING_DIM), normalized
    chunks: list[Chunk]
    nodes: list[Node]
    client: genai.Client


def _chunk_markdown(text: str, source: str = "cv") -> list[Chunk]:
    """Split markdown into chunks by ## headers.

    Each chunk contains the header and its content until the next header.
    Small chunks (< 20 chars of content) are merged with the previous one.
    """
    chunks = []
    # Split by ## headers (level 2)
    sections = re.split(r'\n(?=## )', text)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract header
        lines = section.split('\n', 1)
        header = lines[0].strip().lstrip('#').strip()
        content = lines[1].strip() if len(lines) > 1 else ""

        if not content or len(content) < 20:
            # Too small — merge with previous if possible
            if chunks and len(content) > 0:
                chunks[-1].text += f"\n\n{section}"
            continue

        chunks.append(Chunk(
            text=section,
            source=source,
            section=header,
        ))

    return chunks


def _infer_project_category(project: dict) -> str:
    """Return explicit project category or the current portfolio default."""
    if project.get("category"):
        return project["category"]
    return "backend"


def _project_to_node(project: dict) -> Node:
    """Normalize a projects.json entry to the shared node shape."""
    return Node(
        id=project.get("id", ""),
        type="project",
        name=project.get("name", "Unknown"),
        category=_infer_project_category(project),
        is_central=bool(project.get("is_central", False)),
        data=project,
    )


def _experience_to_node(experience: dict) -> Node:
    """Normalize an experiences.json entry to the shared node shape."""
    node_type = experience.get("type", "experience")
    return Node(
        id=experience.get("id", ""),
        type=node_type,
        name=experience.get("name", "Unknown"),
        category=experience.get("category", node_type),
        is_central=bool(experience.get("is_central", False)),
        data=experience,
    )


def _node_text(node: Node) -> str:
    """Create a natural-language representation optimized for embedding."""
    data = node.data
    text_parts = [
        f"Nodo: {node.name}",
        f"Tipo: {node.type}",
        f"Categoría: {node.category}",
    ]

    if data.get("role"):
        text_parts.append(f"Rol: {data['role']}")

    if data.get("company"):
        text_parts.append(f"Empresa: {data['company']}")

    if data.get("institution"):
        text_parts.append(f"Institución: {data['institution']}")

    if data.get("period"):
        text_parts.append(f"Periodo: {data['period']}")

    if data.get("location"):
        text_parts.append(f"Ubicación: {data['location']}")

    description = data.get("description") or data.get("summary")
    if description:
        text_parts.append(f"Descripción: {description}")

    if data.get("highlights"):
        text_parts.append("Características principales:")
        for highlight in data["highlights"]:
            text_parts.append(f"  - {highlight}")

    if data.get("stack"):
        text_parts.append(f"Stack tecnológico: {', '.join(data['stack'])}")

    if data.get("demonstrates"):
        text_parts.append(f"Demuestra: {', '.join(data['demonstrates'])}")

    if data.get("url"):
        text_parts.append(f"URL: {data['url']}")

    if data.get("status"):
        text_parts.append(f"Estado: {data['status']}")

    return "\n".join(text_parts)


def _chunk_nodes(nodes: list[Node]) -> list[Chunk]:
    """Create one searchable chunk per non-central node.

    Central anchors are intentionally excluded from embeddings/scoring so they
    can stay fixed in the constellation instead of competing for relevance.
    """
    chunks = []
    for node in nodes:
        if node.is_central:
            continue

        chunks.append(Chunk(
            text=_node_text(node),
            source=node.type,
            section=node.name,
            metadata={
                "id": node.id,
                "type": node.type,
                "name": node.name,
                "category": node.category,
                "is_central": node.is_central,
                "data": node.data,
                "url": node.data.get("url", ""),
                "status": node.data.get("status", ""),
            },
        ))

    return chunks


def _validate_nodes(nodes: list[Node]) -> None:
    """Fail fast on invalid node IDs before building embeddings."""
    seen: set[str] = set()
    for node in nodes:
        if not node.id:
            raise ValueError(f"Portfolio node without id: {node.name}")
        if node.id in seen:
            raise ValueError(f"Duplicate portfolio node id: {node.id}")
        seen.add(node.id)


def _embed_texts(client: genai.Client, texts: list[str]) -> np.ndarray:
    """Generate embeddings for a list of texts using Gemini.

    Args:
        client: google-genai Client instance.
        texts: List of text strings to embed.

    Returns:
        Normalized embedding matrix of shape (len(texts), EMBEDDING_DIM).
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )

    vectors = np.array(
        [e.values for e in response.embeddings],
        dtype=np.float32,
    )

    # Normalize for cosine similarity (dot product of unit vectors)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)  # avoid division by zero
    vectors = vectors / norms

    return vectors


def build_index(data_dir: str = "./data") -> RAGIndex:
    """Build the RAG index from normalized portfolio node data.

    Args:
        data_dir: Path to the data directory containing projects.json and
            optionally experiences.json.

    Returns:
        RAGIndex with embedding matrix, chunks, and the genai client.
    """
    data_path = Path(data_dir)
    all_nodes: list[Node] = []

    # ─── Load Projects ───────────────────────────────────
    projects_path = data_path / "projects.json"
    if projects_path.exists():
        with open(projects_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
        project_nodes = [_project_to_node(project) for project in projects]
        all_nodes.extend(project_nodes)
        logger.info(f"Loaded projects: {len(project_nodes)} nodes from {projects_path}")
    else:
        logger.warning(f"Projects file not found: {projects_path}")

    # ─── Load Experiences ────────────────────────────────
    experiences_path = data_path / "experiences.json"
    if experiences_path.exists():
        with open(experiences_path, "r", encoding="utf-8") as f:
            experiences = json.load(f)
        experience_nodes = [_experience_to_node(experience) for experience in experiences]
        all_nodes.extend(experience_nodes)
        logger.info(f"Loaded experiences: {len(experience_nodes)} nodes from {experiences_path}")
    else:
        logger.info(f"Experiences file not found: {experiences_path}")

    _validate_nodes(all_nodes)
    all_chunks = _chunk_nodes(all_nodes)

    if not all_chunks:
        logger.error("No data found to index!")
        raise ValueError("No searchable data available for indexing.")

    # ─── Generate embeddings via Gemini ───────────────────
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY not configured. Cannot generate embeddings.")

    client = genai.Client(api_key=api_key)

    texts = [chunk.text for chunk in all_chunks]
    logger.info(f"Generating embeddings for {len(texts)} chunks via Gemini {EMBEDDING_MODEL}...")
    embeddings = _embed_texts(client, texts)
    logger.info(f"Index built: {embeddings.shape[0]} vectors (dim={embeddings.shape[1]})")

    return RAGIndex(
        embeddings=embeddings,
        chunks=all_chunks,
        nodes=all_nodes,
        client=client,
    )
