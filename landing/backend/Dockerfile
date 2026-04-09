FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies (no build-essential needed — pure Python packages)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (data/ excluded via .dockerignore, mounted as volume)
COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
