"""
indexer.py — RAG Index Builder

Loads CV (markdown) and projects (JSON), chunks them semantically,
generates embeddings with sentence-transformers, and builds a FAISS index.

The index is built in-memory on startup. Given the small dataset size
(CV + a few projects), persistence to disk is unnecessary — rebuilding
takes only a few seconds.
"""

import json
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ─── Embedding model ─────────────────────────────────────────
# all-MiniLM-L6-v2: fast, 384-dim, great for semantic search
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@dataclass
class Chunk:
    """A chunk of text with metadata for RAG retrieval."""
    text: str
    source: str  # "cv" or "project"
    section: str  # header or project name
    metadata: dict = field(default_factory=dict)


@dataclass
class RAGIndex:
    """Container for the FAISS index and associated chunks."""
    faiss_index: faiss.IndexFlatIP
    chunks: list[Chunk]
    embedder: SentenceTransformer


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


def build_index(data_dir: str = "./data") -> RAGIndex:
    """Build the complete RAG index from CV and projects data.

    Args:
        data_dir: Path to the data directory containing cv.md and projects.json.

    Returns:
        RAGIndex with FAISS index, chunks, and the embedding model.
    """
    data_path = Path(data_dir)
    all_chunks: list[Chunk] = []

    # ─── Load CV ──────────────────────────────────────────
    cv_path = data_path / "cv.md"
    if cv_path.exists():
        cv_text = cv_path.read_text(encoding="utf-8")
        cv_chunks = _chunk_markdown(cv_text, source="cv")
        all_chunks.extend(cv_chunks)
        logger.info(f"Loaded CV: {len(cv_chunks)} chunks from {cv_path}")
    else:
        logger.warning(f"CV file not found: {cv_path}")

    # ─── Load Projects ────────────────────────────────────
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
        raise ValueError("No data available for indexing. Check data/ directory.")

    # ─── Generate embeddings ──────────────────────────────
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    texts = [chunk.text for chunk in all_chunks]
    logger.info(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype=np.float32)

    # ─── Build FAISS index ────────────────────────────────
    # Using IndexFlatIP (Inner Product) with normalized vectors = cosine similarity
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)
    logger.info(f"FAISS index built with {index.ntotal} vectors (dim={EMBEDDING_DIM})")

    return RAGIndex(
        faiss_index=index,
        chunks=all_chunks,
        embedder=embedder,
    )
