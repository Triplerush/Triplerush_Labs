FROM python:3.11.15-slim

WORKDIR /app

# Install Python dependencies (no build-essential needed — pure Python packages)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    # Remove pip, setuptools, wheel — not needed at runtime (~20 MB)
    && pip uninstall -y pip setuptools wheel \
    # Clean Python cache files
    && find /usr/local/lib/python3.11 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
    true

# Copy application code (data/ excluded via .dockerignore, mounted as volume)
COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
