"""
Portfolio Chatbot Backend — FastAPI

Endpoints:
  GET  /health   → Health check
  POST /v1/chat  → Chatbot RAG endpoint with SSE streaming

Architecture reference: GUIA_PORTFOLIO_ORQUESTADOR.md → "Arquitectura del Chatbot"

Implementation note: Uses google-genai SDK directly instead of LangChain.
See guide note in Fase 2 section for rationale.
"""

import json
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import datetime

from rag.indexer import build_index, RAGIndex
from rag.agent import generate_response

# ─── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Rate Limiting ────────────────────────────────────────────
RATE_LIMIT_MAX = 20  # max messages per window
RATE_LIMIT_WINDOW = 60  # seconds

# In-memory rate limiter: {ip: [timestamp1, timestamp2, ...]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(client_ip: str) -> bool:
    """Check if a client IP has exceeded the rate limit.

    Returns True if the request is allowed, False if rate-limited.
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old entries
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip]
        if ts > window_start
    ]

    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
        return False

    _rate_limit_store[client_ip].append(now)
    return True


# ─── Input Sanitization ──────────────────────────────────────
MAX_MESSAGE_LENGTH = 500
MAX_HISTORY_LENGTH = 10


def _sanitize_message(message: str) -> str:
    """Sanitize user input: strip whitespace, limit length."""
    message = message.strip()
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH]
    return message


# ─── RAG Index (global) ──────────────────────────────────────
rag_index: RAGIndex | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the RAG index on startup."""
    global rag_index
    logger.info("Building RAG index...")
    try:
        rag_index = build_index(data_dir="./data")
        logger.info("RAG index ready!")
    except Exception as e:
        logger.error(f"Failed to build RAG index: {e}", exc_info=True)
        logger.warning("Chatbot will run in degraded mode (no RAG context)")
    yield
    logger.info("Shutting down chatbot backend.")


# ─── FastAPI App ──────────────────────────────────────────────
app = FastAPI(
    title="Portfolio Chatbot API",
    description="AI chatbot powered by RAG over CV and project data",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS — allow landing frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Models ──────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


# ─── Endpoints ────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check endpoint — always returns OK."""
    return {
        "status": "healthy",
        "service": "portfolio-chatbot",
        "rag_ready": rag_index is not None,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.post("/v1/chat")
async def chat(request: Request, body: ChatRequest):
    """Chatbot RAG endpoint with SSE streaming.

    Request body:
      {
        "message": "¿Qué proyectos tienes?",
        "history": [
          {"role": "user", "content": "Hola"},
          {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
        ]
      }

    Response: SSE stream with events:
      data: {"type": "token", "content": "..."}
      data: {"type": "done"}
      data: {"type": "error", "message": "..."}
    """
    # ─── Rate limiting ────────────────────────────────────
    # Use X-Real-IP from Nginx, fallback to client host
    client_ip = request.headers.get("X-Real-IP", request.client.host)

    if not _check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Máximo {RATE_LIMIT_MAX} mensajes por minuto. "
                           "Espera un momento e intenta de nuevo.",
            },
        )

    # ─── Sanitize input ──────────────────────────────────
    message = _sanitize_message(body.message)
    if not message:
        raise HTTPException(
            status_code=400,
            detail={"error": "Empty message", "message": "El mensaje no puede estar vacío."},
        )

    # ─── Check RAG index ─────────────────────────────────
    if rag_index is None:
        logger.error("RAG index not available")
        fallback_event = json.dumps({
            "type": "error",
            "message": "El chatbot está iniciándose. Intenta de nuevo en unos segundos.",
        })

        async def error_stream():
            yield f"data: {fallback_event}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # ─── Stream response ─────────────────────────────────
    history = [{"role": m.role, "content": m.content} for m in body.history]

    return StreamingResponse(
        generate_response(
            message=message,
            rag_index=rag_index,
            history=history,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Tell Nginx not to buffer SSE
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
