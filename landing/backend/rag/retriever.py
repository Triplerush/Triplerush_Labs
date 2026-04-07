"""
retriever.py — Semantic Search Retriever (Fase 2)

This module will be responsible for:

1. Loading the pre-built FAISS/ChromaDB index (from indexer.py)

2. Performing semantic search:
   - Receive a user query (natural language)
   - Generate query embedding using the same model as indexing
   - Find top-K most similar chunks in the vector store
   - Return ranked results with metadata and relevance scores

3. Re-ranking (optional enhancement):
   - Apply cross-encoder re-ranking for higher precision
   - Filter by metadata (e.g., only project data, only CV data)

4. Context assembly:
   - Format retrieved chunks into a context string
   - Include source references for transparency

Usage (future):
    from rag.retriever import retrieve_context
    context = retrieve_context(query="¿Qué experiencia tienes con RAG?", top_k=5)

Dependencies:
    - faiss-cpu or chromadb (vector store)
    - sentence-transformers (query embedding)
"""

# TODO: Implement in Fase 2
