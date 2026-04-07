"""
indexer.py — RAG Index Builder (Fase 2)

This module will be responsible for:

1. Loading source data:
   - data/cv.md → Fernando's CV in markdown format
   - data/projects.json → Metadata of all portfolio projects

2. Chunking the documents:
   - Split markdown by sections (headers)
   - Split JSON entries into individual project chunks
   - Add metadata (source, section, project_id) to each chunk

3. Generating embeddings:
   - Use sentence-transformers (all-MiniLM-L6-v2 or similar)
   - Generate dense vector embeddings for each chunk

4. Building the vector store:
   - Index embeddings into FAISS (or ChromaDB as alternative)
   - Persist the index to disk for fast loading

Usage (future):
    from rag.indexer import build_index
    index = build_index(data_dir="./data")

Dependencies:
    - langchain (document loaders, text splitters)
    - sentence-transformers (embedding model)
    - faiss-cpu or chromadb (vector store)
"""

# TODO: Implement in Fase 2
