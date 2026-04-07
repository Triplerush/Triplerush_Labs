"""
agent.py — Conversational AI Agent (Fase 2)

This module will be responsible for:

1. Receiving user messages from the /v1/chat endpoint

2. RAG-augmented response generation:
   - Use retriever.py to fetch relevant context
   - Construct a system prompt with:
     • Fernando's professional identity and tone
     • Retrieved context from CV and projects
     • Guardrails against hallucination
   - Call the LLM (Gemini 2.0 Flash via LangChain)

3. Streaming via SSE (Server-Sent Events):
   - Stream tokens as they're generated
   - Send structured SSE events:
     • data: {"type": "token", "content": "..."}
     • data: {"type": "done"}
     • data: {"type": "error", "message": "..."}

4. Conversation management:
   - Maintain short-term context (last N messages)
   - Stateless per request (context from client)

5. Safety and quality:
   - Rate limiting: max 20 messages/minute per IP
   - Input sanitization to prevent prompt injection
   - Fallback message if LLM fails
   - Response caching for common questions

Usage (future):
    from rag.agent import generate_response
    async for chunk in generate_response(message="¿Qué proyectos tienes?", history=[]):
        yield chunk

Dependencies:
    - langchain + langchain-google-genai (LLM)
    - rag.retriever (context retrieval)
"""

# TODO: Implement in Fase 2
