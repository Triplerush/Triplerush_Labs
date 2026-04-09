"""
retriever.py — Semantic Search Retriever

Uses the NumPy embedding matrix built by indexer.py to find the most
relevant chunks for a given user query using cosine similarity.
Embeddings are generated via Gemini gemini-embedding-001.
"""

import logging
import os

import numpy as np
from google import genai
from google.genai import types

from rag.indexer import RAGIndex, Chunk, EMBEDDING_MODEL, EMBEDDING_DIM

logger = logging.getLogger(__name__)


def _embed_query(client: genai.Client, query: str) -> np.ndarray:
    """Generate a normalized embedding for a single query.

    Uses RETRIEVAL_QUERY task type (optimized for queries, not documents).
    """
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )

    vector = np.array(response.embeddings[0].values, dtype=np.float32)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector


def retrieve(
    query: str,
    rag_index: RAGIndex,
    top_k: int = 5,
    min_score: float = 0.15,
) -> list[dict]:
    """Retrieve the most relevant chunks for a user query.

    Args:
        query: Natural language question from the user.
        rag_index: The RAGIndex containing embeddings, chunks, and genai client.
        top_k: Maximum number of chunks to return.
        min_score: Minimum cosine similarity score to include a result.

    Returns:
        List of dicts with keys: text, source, section, score, metadata.
    """
    # Generate query embedding via Gemini
    query_vector = _embed_query(rag_index.client, query)

    # Cosine similarity = dot product of normalized vectors
    scores = rag_index.embeddings @ query_vector

    # Get top-k indices sorted by score (descending)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = float(scores[idx])
        if score < min_score:
            continue

        chunk: Chunk = rag_index.chunks[idx]
        results.append({
            "text": chunk.text,
            "source": chunk.source,
            "section": chunk.section,
            "score": score,
            "metadata": chunk.metadata,
        })

    logger.debug(
        f"Retrieved {len(results)} chunks for query: '{query[:50]}...' "
        f"(top score: {results[0]['score']:.3f})" if results else
        f"No results for query: '{query[:50]}...'"
    )

    return results


def format_context(results: list[dict]) -> str:
    """Format retrieved chunks into a context string for the LLM prompt.

    Args:
        results: List of retrieval results from retrieve().

    Returns:
        Formatted context string with source annotations.
    """
    if not results:
        return "No se encontró contexto relevante."

    context_parts = []
    for i, result in enumerate(results, 1):
        source_label = "CV" if result["source"] == "cv" else "Proyecto"
        context_parts.append(
            f"[Fuente {i}: {source_label} — {result['section']}]\n"
            f"{result['text']}\n"
        )

    return "\n---\n".join(context_parts)
