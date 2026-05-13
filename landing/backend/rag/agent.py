"""
agent.py — Conversational AI Agent

Orchestrates the RAG pipeline: receives a user message, retrieves
relevant context, constructs a prompt, and streams the LLM response
using DigitalOcean Serverless Inference via the OpenAI-compatible SDK.
"""

import json
import logging
import os
from typing import Generator

from openai import OpenAI

from rag.indexer import RAGIndex
from rag.retriever import retrieve, format_context

logger = logging.getLogger(__name__)

# ─── System Prompt ────────────────────────────────────────────
SYSTEM_PROMPT = """Eres el asistente virtual del portfolio de Fernando, un AI Software Engineer.

Tu rol es responder preguntas sobre el portfolio de Fernando: proyectos desplegados, experiencia laboral, formación, certificaciones y capacidades técnicas que estén presentes en el contexto recuperado.

REGLAS IMPORTANTES:
1. SOLO responde con información que esté en el contexto proporcionado. Si la información no está en el contexto, di honestamente que no tienes esa información y sugiere contactar a Fernando directamente.
2. NUNCA inventes proyectos, experiencias, certificaciones, features ni datos que no estén en el contexto.
3. Responde en el MISMO IDIOMA que el usuario use para preguntar (español si preguntan en español, inglés si preguntan en inglés).
4. Sé breve pero informativo. No repitas información innecesariamente.
5. Cuando hables de proyectos, menciona el stack tecnológico, las features principales y qué demuestra cada uno. Cuando hables de experiencia o formación, resume el rol, los highlights y las tecnologías relevantes del contexto.
6. Si te preguntan sobre temas fuera del portfolio de Fernando o sobre datos no presentes en el contexto, indícalo honestamente y sugiere contactar a Fernando directamente para otras consultas.
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


_llm_client: OpenAI | None = None


def _get_llm_client() -> OpenAI:
    """Lazy-initialized OpenAI-compatible client.

    Provider-agnostic: works with any OpenAI-compatible endpoint (DigitalOcean
    Serverless Inference, Together, Groq, OpenRouter, OpenAI, Ollama local).
    Swap provider by changing LLM_BASE_URL + LLM_MODEL.
    """
    global _llm_client
    if _llm_client is None:
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError(
                "LLM_API_KEY no está configurado. "
                "Configura la API key del proveedor OpenAI-compatible."
            )
        base_url = os.getenv(
            "LLM_BASE_URL", "https://inference.do-ai.run/v1"
        )
        _llm_client = OpenAI(api_key=api_key, base_url=base_url)
    return _llm_client


def _build_messages(
    user_message: str,
    context: str,
    history: list[dict] | None = None,
) -> list[dict]:
    """Build the OpenAI-style message list (system + history + user)."""
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history[-6:]:
            role = msg.get("role")
            if role not in ("user", "assistant"):
                continue
            messages.append({"role": role, "content": msg.get("content", "")})

    augmented_message = (
        f"Contexto relevante de mi portfolio:\n"
        f"---\n{context}\n---\n\n"
        f"Pregunta del usuario: {user_message}"
    )
    messages.append({"role": "user", "content": augmented_message})

    return messages


def generate_response(
    message: str,
    rag_index: RAGIndex,
    history: list[dict] | None = None,
) -> Generator[str, None, None]:
    """Generate a streaming RAG response as SSE events."""
    try:
        results = retrieve(query=message, rag_index=rag_index, top_k=5)
        context = format_context(results)

        logger.info(
            f"Chat query: '{message[:80]}...' | "
            f"Retrieved {len(results)} chunks"
        )

        messages = _build_messages(message, context, history)

        client = _get_llm_client()
        model_name = os.getenv("LLM_MODEL", "openai-gpt-oss-120b")

        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                event = json.dumps({"type": "token", "content": content})
                yield f"data: {event}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        error_event = json.dumps({"type": "error", "message": FALLBACK_MESSAGE})
        yield f"data: {error_event}\n\n"
