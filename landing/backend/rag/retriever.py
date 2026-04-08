"""
retriever.py — Semantic Search Retriever

Uses the FAISS index built by indexer.py to find the most relevant
chunks for a given user query using cosine similarity.
"""

import logging
import numpy as np

from rag.indexer import RAGIndex, Chunk

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    rag_index: RAGIndex,
    top_k: int = 5,
    min_score: float = 0.15,
) -> list[dict]:
    """Retrieve the most relevant chunks for a user query.

    Args:
        query: Natural language question from the user.
        rag_index: The RAGIndex containing FAISS index, chunks, and embedder.
        top_k: Maximum number of chunks to return.
        min_score: Minimum cosine similarity score to include a result.

    Returns:
        List of dicts with keys: text, source, section, score, metadata.
    """
    # Generate query embedding (same model as indexing)
    query_embedding = rag_index.embedder.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    query_embedding = np.array(query_embedding, dtype=np.float32)

    # Search FAISS index
    scores, indices = rag_index.faiss_index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or score < min_score:
            continue

        chunk: Chunk = rag_index.chunks[idx]
        results.append({
            "text": chunk.text,
            "source": chunk.source,
            "section": chunk.section,
            "score": float(score),
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
