<template>
  <!--
    ╔═══════════════════════════════════════════════════════════╗
    ║  ChatWidget.vue — Fase 3 Placeholder                     ║
    ║                                                           ║
    ║  This component will contain the floating AI chatbot      ║
    ║  widget (bottom-right corner). It will connect to the     ║
    ║  FastAPI backend at POST /v1/chat with SSE streaming.     ║
    ║                                                           ║
    ║  Planned features:                                        ║
    ║  - Floating bubble that expands into chat window          ║
    ║  - Welcome message: "Pregúntame sobre mis proyectos"      ║
    ║  - SSE streaming for real-time responses                  ║
    ║  - Suggested questions:                                   ║
    ║    • "¿Qué tecnologías usas?"                             ║
    ║    • "¿Tu proyecto más reciente?"                         ║
    ║    • "¿Por qué debería contratarte?"                      ║
    ║  - Conversation persistence in sessionStorage             ║
    ║  - "Thinking..." indicator with animation                 ║
    ║  - Toggle open/close                                      ║
    ║                                                           ║
    ║  DO NOT implement until Fase 2 (backend) is complete.     ║
    ╚═══════════════════════════════════════════════════════════╝
  -->

  <!-- Placeholder: chat bubble indicator -->
  <div class="fixed bottom-6 right-6 z-50" id="chat-widget-placeholder">
    <div class="w-14 h-14 rounded-full flex items-center justify-center shadow-lg cursor-pointer
                transition-all duration-300 hover:scale-110 animate-pulse-glow opacity-60 hover:opacity-100"
         style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));"
         title="AI Chat — Coming Soon (Fase 3)">
      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    </div>
  </div>
</template>

<script setup>
// Fase 3: This component will be fully implemented after the chatbot
// backend (Fase 2) is functional at POST /v1/chat.
//
// Architecture reference: GUIA_PORTFOLIO_ORQUESTADOR.md → "Arquitectura del Chatbot"
//
// Implementation plan:
// 1. ChatWidget state: open/closed, messages[], isThinking
// 2. SSE connection to /v1/chat endpoint
// 3. Message rendering with markdown support
// 4. Suggested questions as quick-reply buttons
// 5. sessionStorage persistence for conversation continuity
</script>
