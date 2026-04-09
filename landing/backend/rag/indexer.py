"""
indexer.py — RAG Index Builder

Loads deployed projects (JSON), generates embeddings with Gemini
gemini-embedding-001 via google-genai, and builds an in-memory
cosine-similarity index using NumPy.

Only indexes projects.json — the chatbot should only know about
projects that are actually deployed in the portfolio.

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
    source: str  # "cv" or "project"
    section: str  # header or project name
    metadata: dict = field(default_factory=dict)


@dataclass
class RAGIndex:
    """Container for the embedding matrix and associated chunks."""
    embeddings: np.ndarray  # shape: (n_chunks, EMBEDDING_DIM), normalized
    chunks: list[Chunk]
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


def _chunk_projects(projects: list[dict]) -> list[Chunk]:
    """Create one chunk per project from projects.json.

    Each chunk contains a natural-language summary of the project
    optimized for semantic search.
    """
    chunks = []
    for project in projects:
        # Build a rich text representation for embedding
        text_parts = [
            f"Proyecto: {project.get('name', 'Unknown')}",
            f"Descripción: {project.get('description', '')}",
        ]

        if project.get('highlights'):
            text_parts.append("Características principales:")
            for h in project['highlights']:
                text_parts.append(f"  - {h}")

        if project.get('stack'):
            text_parts.append(f"Stack tecnológico: {', '.join(project['stack'])}")

        if project.get('demonstrates'):
            text_parts.append(f"Demuestra: {', '.join(project['demonstrates'])}")

        if project.get('url'):
            text_parts.append(f"URL: {project['url']}")

        if project.get('status'):
            text_parts.append(f"Estado: {project['status']}")

        chunks.append(Chunk(
            text='\n'.join(text_parts),
            source="project",
            section=project.get('name', 'Unknown'),
            metadata={
                "id": project.get("id", ""),
                "url": project.get("url", ""),
                "status": project.get("status", ""),
            },
        ))

    return chunks


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
    """Build the RAG index from deployed projects data.

    Only indexes projects.json (deployed projects). The chatbot should only
    have context about projects that are actually live in the portfolio.

    Args:
        data_dir: Path to the data directory containing projects.json.

    Returns:
        RAGIndex with embedding matrix, chunks, and the genai client.
    """
    data_path = Path(data_dir)
    all_chunks: list[Chunk] = []

    # ─── Load Projects (only deployed) ────────────────────
    projects_path = data_path / "projects.json"
    if projects_path.exists():
        with open(projects_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
        project_chunks = _chunk_projects(projects)
        all_chunks.extend(project_chunks)
        logger.info(f"Loaded projects: {len(project_chunks)} chunks from {projects_path}")
    else:
        logger.warning(f"Projects file not found: {projects_path}")

    if not all_chunks:
        logger.error("No data found to index!")
        raise ValueError("No data available for indexing. Check data/projects.json.")

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
        client=client,
    )
