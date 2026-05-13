FROM python:3.11.15-slim

WORKDIR /app

ARG EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Install Python dependencies (fastembed brings ONNX runtime, no torch)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model into the image so first request stays fast
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='${EMBEDDING_MODEL}')"

# Trim runtime: remove pip/setuptools/wheel and pyc caches
RUN pip uninstall -y pip setuptools wheel \
    && find /usr/local/lib/python3.11 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
    true

# Copy application code (data/ excluded via .dockerignore, mounted as volume)
COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
