"""
Portfolio Chatbot Backend — FastAPI

Endpoints:
  GET  /health   → Health check (functional)
  POST /v1/chat  → Chatbot RAG endpoint (Fase 2 — placeholder)

Architecture reference: GUIA_PORTFOLIO_ORQUESTADOR.md → "Arquitectura del Chatbot"
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import datetime

app = FastAPI(
    title="Portfolio Chatbot API",
    description="AI chatbot powered by RAG over CV and project data",
    version="0.1.0",
)

# CORS — allow landing frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint — always returns OK."""
    return {
        "status": "healthy",
        "service": "portfolio-chatbot",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.post("/v1/chat")
async def chat(request: Request):
    """
    Chatbot RAG endpoint — Fase 2 placeholder.

    When implemented, this will:
    1. Receive a user question
    2. Retrieve relevant context from the FAISS/ChromaDB vector store
    3. Construct a prompt with the retrieved context
    4. Stream the LLM response back via SSE

    Request body:
      { "message": "¿Qué proyectos tienes?" }

    Response (future): SSE stream with generated answer
    Response (current): 501 Not Implemented
    """
    return JSONResponse(
        status_code=501,
        content={
            "error": "Coming soon",
            "message": "The chatbot backend is under development (Fase 2). "
                       "Check back soon!",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
