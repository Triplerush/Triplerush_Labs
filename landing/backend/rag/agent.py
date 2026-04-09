"""
agent.py — Conversational AI Agent

Orchestrates the RAG pipeline: receives a user message, retrieves
relevant context, constructs a prompt, and streams the LLM response
using Gemini via the google-genai SDK (reusing the client from RAGIndex).
"""

import json
import logging
import os
from typing import Generator

from google.genai import types as genai_types

from rag.indexer import RAGIndex
from rag.retriever import retrieve, format_context

logger = logging.getLogger(__name__)

# ─── System Prompt ────────────────────────────────────────────
SYSTEM_PROMPT = """Eres el asistente virtual del portfolio de Fernando, un AI Software Engineer.

Tu rol es responder preguntas sobre Fernando: su experiencia, proyectos, habilidades técnicas, formación y carrera profesional. Responde de manera profesional, concisa y útil.

REGLAS IMPORTANTES:
1. SOLO responde con información que esté en el contexto proporcionado. Si la información no está en el contexto, di honestamente que no tienes esa información y sugiere contactar a Fernando directamente.
2. NUNCA inventes experiencia, proyectos, empresas ni datos que no estén en el contexto.
3. Responde en el MISMO IDIOMA que el usuario use para preguntar (español si preguntan en español, inglés si preguntan en inglés).
4. Sé breve pero informativo. No repitas información innecesariamente.
5. Cuando hables de proyectos, menciona el stack tecnológico y qué demuestra cada uno.
6. Si te preguntan algo personal que no sea profesional, redirige educadamente al ámbito profesional.
7. Puedes usar markdown en tus respuestas (bold, listas, etc.) para hacerlas más legibles.
8. Si mencionas un proyecto que tiene URL, inclúyela para que el usuario pueda verlo.

IDENTIDAD:
- Nombre: Fernando
- Título: AI Software Engineer
- Tagline: "Building AI that ships to production"
- Enfoque: Bridging ML, DevOps, and AI Engineering para crear sistemas inteligentes que escalan."""


FALLBACK_MESSAGE = (
    "Lo siento, estoy teniendo problemas técnicos en este momento. "
    "Puedes contactar a Fernando directamente a través de los enlaces "
    "de contacto en la página. ¡Disculpa la molestia!"
)


def _build_messages(
    user_message: str,
    context: str,
    history: list[dict] | None = None,
) -> list[dict]:
    """Build the message list for the LLM call.

    Args:
        user_message: Current user question.
        context: Retrieved RAG context.
        history: Previous conversation messages [{"role": "user"|"assistant", "content": "..."}].

    Returns:
        List of message dicts for the google-genai API.
    """
    messages = []

    # Include recent history (last 6 messages max to stay within context window)
    if history:
        for msg in history[-6:]:
            role = "user" if msg.get("role") == "user" else "model"
            messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })

    # Current user message with RAG context injected
    augmented_message = (
        f"Contexto relevante de mi portfolio:\n"
        f"---\n{context}\n---\n\n"
        f"Pregunta del usuario: {user_message}"
    )
    messages.append({
        "role": "user",
        "parts": [{"text": augmented_message}],
    })

    return messages


def generate_response(
    message: str,
    rag_index: RAGIndex,
    history: list[dict] | None = None,
) -> Generator[str, None, None]:
    """Generate a streaming RAG response as SSE events.

    This is a sync generator intentionally — FastAPI's StreamingResponse
    runs sync generators in a threadpool, avoiding event loop blocking
    during the synchronous Google API calls.

    Args:
        message: User's question.
        rag_index: The RAGIndex for context retrieval.
        history: Previous conversation messages.

    Yields:
        SSE-formatted strings:
        - data: {"type": "token", "content": "..."}
        - data: {"type": "done"}
        - data: {"type": "error", "message": "..."}
    """
    try:
        # ─── 1. Retrieve relevant context ─────────────────
        results = retrieve(query=message, rag_index=rag_index, top_k=5)
        context = format_context(results)

        logger.info(
            f"Chat query: '{message[:80]}...' | "
            f"Retrieved {len(results)} chunks"
        )

        # ─── 2. Build prompt ──────────────────────────────
        messages = _build_messages(message, context, history)

        # ─── 3. Call Gemini with streaming ────────────────
        model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")

        # Reuse the client already created during index build
        client = rag_index.client

        response = client.models.generate_content_stream(
            model=model_name,
            contents=messages,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )

        # ─── 4. Stream tokens ────────────────────────────
        for chunk in response:
            if chunk.text:
                event = json.dumps({"type": "token", "content": chunk.text})
                yield f"data: {event}\n\n"

        # ─── 5. Done event ────────────────────────────────
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        error_event = json.dumps({"type": "error", "message": FALLBACK_MESSAGE})
        yield f"data: {error_event}\n\n"
