<template>
  <div id="chat-widget" class="fixed bottom-6 right-6 z-50">

    <!-- ─── Welcome Tooltip ─────────────────────────────── -->
    <transition name="chat-tooltip">
      <div v-if="showWelcome && !isOpen"
           class="absolute bottom-18 right-0 whitespace-nowrap px-4 py-2.5 rounded-xl text-sm font-medium shadow-xl pointer-events-none chat-tooltip"
           :class="theme === 'dark'
             ? 'bg-surface-800 text-white/90 border border-white/10'
             : 'bg-white text-gray-800 border border-black/10'">
        <span>💬 Pregúntame sobre mis proyectos</span>
        <div class="absolute -bottom-1.5 right-6 w-3 h-3 rotate-45"
             :class="theme === 'dark' ? 'bg-surface-800 border-r border-b border-white/10' : 'bg-white border-r border-b border-black/10'"></div>
      </div>
    </transition>

    <!-- ─── Chat Window ─────────────────────────────────── -->
    <transition name="chat-window">
      <div v-if="isOpen"
           class="absolute bottom-18 right-0 w-[380px] max-w-[calc(100vw-2rem)] rounded-2xl shadow-2xl overflow-hidden flex flex-col chat-panel"
           :class="theme === 'dark'
             ? 'bg-surface-900/95 border border-white/10'
             : 'bg-white/95 border border-black/10'"
           style="height: 520px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);">

        <!-- Header -->
        <div class="flex items-center gap-3 px-5 py-4 border-b shrink-0"
             :class="theme === 'dark' ? 'border-white/10' : 'border-black/10'">
          <div class="relative">
            <div class="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold"
                 style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));">
              AI
            </div>
            <div class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2"
                 :class="theme === 'dark' ? 'border-surface-900' : 'border-white'"></div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold truncate">Fernando AI</p>
            <p class="text-xs opacity-50">Asistente del portfolio</p>
          </div>
          <button @click="clearConversation"
                  class="p-1.5 rounded-lg opacity-40 hover:opacity-100 transition-opacity"
                  title="Limpiar conversación"
                  id="chat-clear-btn">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button @click="isOpen = false"
                  class="p-1.5 rounded-lg opacity-40 hover:opacity-100 transition-opacity"
                  id="chat-close-btn">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer"
             class="flex-1 overflow-y-auto px-4 py-4 space-y-4 chat-messages-scroll"
             :class="theme === 'dark' ? 'chat-scroll-dark' : 'chat-scroll-light'">

          <!-- Welcome message (always first) -->
          <div class="flex gap-3" v-if="messages.length === 0">
            <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0 mt-1"
                 style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));">
              AI
            </div>
            <div class="rounded-2xl rounded-tl-md px-4 py-3 text-sm max-w-[85%]"
                 :class="theme === 'dark'
                   ? 'bg-surface-800 text-white/90'
                   : 'bg-gray-100 text-gray-800'">
              <p>¡Hola! 👋 Soy el asistente AI de Fernando.</p>
              <p class="mt-2">Puedo responder sobre su experiencia, proyectos y tecnologías. ¿En qué puedo ayudarte?</p>
            </div>
          </div>

          <!-- Chat messages -->
          <div v-for="(msg, i) in messages" :key="i"
               class="flex gap-3"
               :class="msg.role === 'user' ? 'justify-end' : ''">

            <!-- Assistant avatar -->
            <div v-if="msg.role === 'assistant'"
                 class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0 mt-1"
                 style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));">
              AI
            </div>

            <!-- Message bubble -->
            <div class="rounded-2xl px-4 py-3 text-sm max-w-[85%] leading-relaxed"
                 :class="msg.role === 'user'
                   ? 'rounded-tr-md text-white bg-gradient-to-br from-brand-500 to-accent-500'
                   : theme === 'dark'
                     ? 'rounded-tl-md bg-surface-800 text-white/90'
                     : 'rounded-tl-md bg-gray-100 text-gray-800'"
                 v-html="msg.role === 'assistant' ? renderMarkdown(msg.content) : escapeHtml(msg.content)">
            </div>
          </div>

          <!-- Thinking indicator -->
          <div v-if="isThinking" class="flex gap-3">
            <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0 mt-1"
                 style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));">
              AI
            </div>
            <div class="rounded-2xl rounded-tl-md px-4 py-3.5"
                 :class="theme === 'dark' ? 'bg-surface-800' : 'bg-gray-100'">
              <div class="flex gap-1.5 items-center">
                <span class="thinking-dot"></span>
                <span class="thinking-dot" style="animation-delay: 0.15s;"></span>
                <span class="thinking-dot" style="animation-delay: 0.3s;"></span>
              </div>
            </div>
          </div>

          <!-- Error message -->
          <div v-if="errorMessage" class="flex justify-center">
            <div class="rounded-xl px-4 py-2.5 text-xs text-center max-w-[90%]"
                 :class="theme === 'dark'
                   ? 'bg-red-900/30 text-red-300 border border-red-500/20'
                   : 'bg-red-50 text-red-600 border border-red-200'">
              {{ errorMessage }}
            </div>
          </div>
        </div>

        <!-- Suggestions (show when no user messages yet) -->
        <div v-if="messages.filter(m => m.role === 'user').length === 0 && !isThinking"
             class="px-4 pb-2 flex flex-wrap gap-2 shrink-0">
          <button v-for="suggestion in suggestions" :key="suggestion"
                  @click="sendMessage(suggestion)"
                  class="text-xs px-3 py-1.5 rounded-full border transition-all duration-200 hover:scale-105 cursor-pointer"
                  :class="theme === 'dark'
                    ? 'border-white/15 text-white/70 hover:border-brand-400/50 hover:text-white hover:bg-brand-500/10'
                    : 'border-black/10 text-gray-600 hover:border-brand-400/50 hover:text-brand-600 hover:bg-brand-50'">
            {{ suggestion }}
          </button>
        </div>

        <!-- Input area -->
        <div class="px-4 py-3 border-t shrink-0"
             :class="theme === 'dark' ? 'border-white/10' : 'border-black/10'">
          <form @submit.prevent="handleSubmit" class="flex gap-2 items-end">
            <div class="flex-1 relative">
              <textarea
                ref="inputRef"
                v-model="inputText"
                @keydown="handleKeyDown"
                :placeholder="isThinking ? 'Esperando respuesta...' : 'Escribe tu pregunta...'"
                :disabled="isThinking"
                rows="1"
                class="w-full resize-none rounded-xl px-4 py-2.5 text-sm outline-none transition-all duration-200 max-h-24"
                :class="theme === 'dark'
                  ? 'bg-surface-800 text-white/90 placeholder-white/30 border border-white/10 focus:border-brand-500/50'
                  : 'bg-gray-100 text-gray-800 placeholder-gray-400 border border-black/5 focus:border-brand-500/50'"
                id="chat-input"
              ></textarea>
            </div>
            <button type="submit"
                    :disabled="!inputText.trim() || isThinking"
                    class="p-2.5 rounded-xl text-white transition-all duration-200 shrink-0 disabled:opacity-30 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
                    style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));"
                    id="chat-send-btn">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 19V5m0 0l-7 7m7-7l7 7" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </transition>

    <!-- ─── Floating Bubble ─────────────────────────────── -->
    <button @click="toggleChat"
            class="w-14 h-14 rounded-full flex items-center justify-center shadow-lg cursor-pointer transition-all duration-300 hover:scale-110 active:scale-95 chat-bubble-btn"
            :class="isOpen ? 'rotate-0' : 'animate-pulse-glow'"
            style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));"
            id="chat-toggle-btn"
            aria-label="Toggle AI Chat">
      <!-- Chat icon (closed state) -->
      <svg v-if="!isOpen" class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
      <!-- Close icon (open state) -->
      <svg v-else class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- Unread indicator -->
    <div v-if="hasUnread && !isOpen"
         class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-500 flex items-center justify-center text-white text-xs font-bold animate-bounce pointer-events-none">
      !
    </div>
  </div>
</template>

<script setup>
import { ref, inject, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

// ─── State ───────────────────────────────────────────────
const theme = inject('theme', ref('dark'))
const isOpen = ref(false)
const showWelcome = ref(true)
const isThinking = ref(false)
const inputText = ref('')
const errorMessage = ref('')
const hasUnread = ref(false)
const messages = ref([])
const messagesContainer = ref(null)
const inputRef = ref(null)

// Controller for aborting fetch requests
let abortController = null

// ─── Suggestions ─────────────────────────────────────────
const suggestions = [
  '¿Qué tecnologías usas?',
  '¿Tu proyecto más reciente?',
  '¿Por qué debería contratarte?',
]

// ─── Session storage key ─────────────────────────────────
const STORAGE_KEY = 'portfolio-chat-messages'

// ─── Lifecycle ───────────────────────────────────────────
onMounted(() => {
  // Restore conversation from sessionStorage
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length > 0) {
        messages.value = parsed
      }
    }
  } catch {
    // Ignore parse errors
  }

  // Auto-dismiss welcome tooltip after 8 seconds
  welcomeTimer = setTimeout(() => {
    showWelcome.value = false
  }, 8000)
})

let welcomeTimer = null

onBeforeUnmount(() => {
  if (welcomeTimer) clearTimeout(welcomeTimer)
  if (abortController) abortController.abort()
})

// ─── Watchers ────────────────────────────────────────────
watch(messages, (newMessages) => {
  // Persist to sessionStorage
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(newMessages))
  } catch {
    // Storage full — ignore
  }
  // Auto-scroll
  scrollToBottom()
}, { deep: true })

watch(isOpen, (opened) => {
  if (opened) {
    showWelcome.value = false
    hasUnread.value = false
    nextTick(() => {
      inputRef.value?.focus()
      scrollToBottom()
    })
  }
})

// ─── Methods ─────────────────────────────────────────────
function toggleChat() {
  isOpen.value = !isOpen.value
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function handleKeyDown(e) {
  // Enter without shift sends the message
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSubmit()
  }
}

function handleSubmit() {
  const text = inputText.value.trim()
  if (!text || isThinking.value) return
  sendMessage(text)
}

async function sendMessage(text) {
  errorMessage.value = ''
  inputText.value = ''

  // Add user message
  messages.value.push({ role: 'user', content: text })

  // Build history (last 10 messages for context)
  const history = messages.value
    .slice(-11, -1) // exclude current message, take up to 10 previous
    .map(m => ({ role: m.role, content: m.content }))

  isThinking.value = true

  // Add placeholder for assistant response
  const assistantIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: '' })

  try {
    // Abort any previous request
    if (abortController) abortController.abort()
    abortController = new AbortController()

    const response = await fetch('/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history }),
      signal: abortController.signal,
    })

    if (response.status === 429) {
      // Rate limited
      messages.value.splice(assistantIndex, 1)
      errorMessage.value = 'Has enviado demasiados mensajes. Espera un momento e intenta de nuevo.'
      isThinking.value = false
      return
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    // Parse SSE stream
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    isThinking.value = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Process complete SSE lines
      const lines = buffer.split('\n')
      buffer = lines.pop() // keep incomplete last line

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue

        const dataStr = line.slice(6).trim()
        if (!dataStr) continue

        try {
          const event = JSON.parse(dataStr)

          if (event.type === 'token') {
            messages.value[assistantIndex].content += event.content
          } else if (event.type === 'done') {
            // Stream complete
          } else if (event.type === 'error') {
            errorMessage.value = event.message || 'Error al procesar la respuesta.'
          }
        } catch {
          // Non-JSON line, skip
        }
      }
    }

    // If assistant message is empty after stream, show fallback
    if (!messages.value[assistantIndex]?.content) {
      messages.value[assistantIndex].content = 'Lo siento, no pude generar una respuesta. Por favor intenta de nuevo.'
    }

    // Mark unread if chat is closed
    if (!isOpen.value) {
      hasUnread.value = true
    }

  } catch (err) {
    if (err.name === 'AbortError') return

    console.error('Chat error:', err)
    isThinking.value = false

    // Remove empty assistant message
    if (messages.value[assistantIndex]?.content === '') {
      messages.value.splice(assistantIndex, 1)
    }

    errorMessage.value = 'No pude conectar con el chatbot. Puedes contactarme directamente por email o LinkedIn.'
  }
}

function clearConversation() {
  messages.value = []
  errorMessage.value = ''
  isThinking.value = false
  if (abortController) abortController.abort()
  try {
    sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // Ignore
  }
}

// ─── Markdown rendering (lightweight) ────────────────────
function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function renderMarkdown(text) {
  if (!text) return ''

  let html = escapeHtml(text)

  // Code blocks: ```...```
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="chat-code-block">$1</pre>')

  // Inline code: `...`
  html = html.replace(/`([^`]+)`/g, '<code class="chat-inline-code">$1</code>')

  // Bold: **...**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Italic: *...*
  html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')

  // Unordered lists: - item
  html = html.replace(/^- (.+)$/gm, '<li class="chat-list-item">$1</li>')
  html = html.replace(/(<li class="chat-list-item">.*<\/li>\n?)+/g, '<ul class="chat-list">$&</ul>')

  // Line breaks
  html = html.replace(/\n/g, '<br>')

  return html
}
</script>

<style scoped>
/* ─── Chat Window Transitions ──────────────────────────── */
.chat-window-enter-active {
  animation: chat-slide-up 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.chat-window-leave-active {
  animation: chat-slide-up 0.25s ease-in reverse;
}

@keyframes chat-slide-up {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ─── Tooltip Transition ────────────────────────────────── */
.chat-tooltip-enter-active {
  animation: tooltip-fade 0.3s ease-out;
}
.chat-tooltip-leave-active {
  animation: tooltip-fade 0.2s ease-in reverse;
}

@keyframes tooltip-fade {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ─── Thinking Dots ─────────────────────────────────────── */
.thinking-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-brand-400);
  animation: thinking-bounce 1.2s ease-in-out infinite;
  opacity: 0.6;
}

@keyframes thinking-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
}

/* ─── Chat Scrollbar ────────────────────────────────────── */
.chat-messages-scroll::-webkit-scrollbar {
  width: 5px;
}
.chat-messages-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.chat-scroll-dark::-webkit-scrollbar-thumb {
  background: oklch(0.40 0.05 250);
  border-radius: 3px;
}
.chat-scroll-light::-webkit-scrollbar-thumb {
  background: oklch(0.75 0.02 250);
  border-radius: 3px;
}

/* ─── Chat Bubble Button ───────────────────────────────── */
.chat-bubble-btn {
  box-shadow: 0 8px 30px oklch(0.55 0.20 250 / 0.35);
}
.chat-bubble-btn:hover {
  box-shadow: 0 12px 40px oklch(0.55 0.20 250 / 0.5);
}

/* ─── Chat Panel Shadow ────────────────────────────────── */
.chat-panel {
  box-shadow: 0 25px 60px oklch(0 0 0 / 0.35), 0 0 0 1px oklch(1 0 0 / 0.05);
}

/* ─── Textarea auto-grow ───────────────────────────────── */
textarea {
  field-sizing: content;
}
</style>

<style>
/* ─── Markdown in chat (global for v-html) ─────────────── */
.chat-code-block {
  display: block;
  background: oklch(0.15 0.02 250 / 0.8);
  color: oklch(0.80 0.10 150);
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  margin: 0.5rem 0;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.light .chat-code-block {
  background: oklch(0.96 0.005 250);
  color: oklch(0.35 0.10 250);
}

.chat-inline-code {
  background: oklch(0.25 0.02 250 / 0.6);
  color: oklch(0.75 0.15 300);
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  font-family: var(--font-mono);
  font-size: 0.85em;
}

.light .chat-inline-code {
  background: oklch(0.94 0.01 250);
  color: oklch(0.45 0.20 300);
}

.chat-list {
  list-style: none;
  padding-left: 0;
  margin: 0.25rem 0;
}

.chat-list-item {
  position: relative;
  padding-left: 1rem;
  margin: 0.15rem 0;
}

.chat-list-item::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-brand-400);
  font-weight: bold;
}
</style>
