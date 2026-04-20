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
             data-lenis-prevent
             class="flex-1 overflow-y-auto px-4 py-4 space-y-4 chat-messages-scroll"
             :class="theme === 'dark' ? 'chat-scroll-dark' : 'chat-scroll-light'"
             @wheel.stop>

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
          <template v-for="(msg, i) in messages" :key="i">
            <div class="flex gap-3"
                 :class="msg.role === 'user' ? 'justify-end' : ''">

              <!-- Assistant avatar -->
              <div v-if="msg.role === 'assistant'"
                   class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0 mt-1 chat-avatar"
                   style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));">
                AI
              </div>

              <!-- Message bubble -->
              <div class="chat-bubble rounded-2xl px-4 py-3 text-sm max-w-[85%] leading-relaxed"
                   :class="[
                     msg.role === 'user'
                       ? 'chat-bubble-user rounded-tr-md text-white'
                       : ['rounded-tl-md chat-bubble-assistant', theme === 'dark' ? 'chat-bubble-assistant-dark' : 'chat-bubble-assistant-light']
                   ]"
                   v-html="msg.role === 'assistant' ? renderMarkdown(msg.content) : escapeHtml(msg.content)">
              </div>
            </div>

            <!-- Project chips (below assistant messages that mention projects) -->
            <div v-if="msg.role === 'assistant' && msg.content"
                 class="flex flex-wrap gap-2 pl-10"
                 :class="mentionedProjects(msg.content).length ? '' : 'hidden'">
              <button v-for="proj in mentionedProjects(msg.content)" :key="proj.id"
                      @click="openProject(proj)"
                      class="chat-project-chip group flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer"
                      :class="theme === 'dark'
                        ? 'bg-surface-800/80 border border-brand-500/30 text-white/90 hover:bg-brand-500/15 hover:border-brand-400/60'
                        : 'bg-white border border-brand-500/30 text-gray-700 hover:bg-brand-50 hover:border-brand-500/60'">
                <svg class="w-3.5 h-3.5 opacity-70 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 11H5m14 0l-4-4m4 4l-4 4" />
                </svg>
                <span>{{ proj.name }}</span>
                <span v-if="proj.status === 'wip'" class="ml-0.5 text-[10px] px-1.5 py-0.5 rounded-full opacity-70"
                      :class="theme === 'dark' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-yellow-100 text-yellow-700'">WIP</span>
              </button>
            </div>
          </template>

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
const projects = inject('projects', ref([]))
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

  // Markdown links: [text](url) — render as styled pill
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/[^\s)]*)\)/g,
    (_, label, url) => {
      const isExternal = /^https?:\/\//.test(url)
      const target = isExternal ? ' target="_blank" rel="noopener noreferrer"' : ''
      const icon = isExternal
        ? '<svg class="chat-link-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>'
        : '<svg class="chat-link-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>'
      return `<a href="${url}" class="chat-link"${target}>${label}${icon}</a>`
    })

  // Headings: ## Title and ### Title
  html = html.replace(/^### (.+)$/gm, '<h4 class="chat-heading chat-heading-sm">$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3 class="chat-heading chat-heading-md">$1</h3>')

  // Bold: **...**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="chat-strong">$1</strong>')

  // Italic: *...*
  html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')

  // Unordered lists: - item
  html = html.replace(/^- (.+)$/gm, '<li class="chat-list-item">$1</li>')
  html = html.replace(/(<li class="chat-list-item">.*<\/li>\n?)+/g, '<ul class="chat-list">$&</ul>')

  // Double newline → paragraph break (visual spacing)
  html = html.replace(/\n{2,}/g, '</p><p class="chat-paragraph">')
  html = `<p class="chat-paragraph">${html}</p>`

  // Single newline → <br>
  html = html.replace(/\n/g, '<br>')

  // Cleanup: empty paragraphs and paragraph wrapping block elements
  html = html.replace(/<p class="chat-paragraph">\s*<\/p>/g, '')
  html = html.replace(/<p class="chat-paragraph">(\s*<(?:ul|pre|h3|h4)[^>]*>)/g, '$1')
  html = html.replace(/(<\/(?:ul|pre|h3|h4)>)(\s*)<\/p>/g, '$1$2')

  return html
}

// ─── Project linking ─────────────────────────────────────
// Detects project mentions (by name or id) in assistant output
// and shows clickable chips below the message.
function mentionedProjects(content) {
  if (!content || !projects.value?.length) return []
  const lower = content.toLowerCase()
  const seen = new Set()
  const found = []
  for (const p of projects.value) {
    if (seen.has(p.id)) continue
    const needles = [p.id, p.name].filter(Boolean).map(s => s.toLowerCase())
    if (needles.some(n => n.length > 2 && lower.includes(n))) {
      found.push(p)
      seen.add(p.id)
    }
  }
  return found
}

function openProject(project) {
  if (!project) return
  const url = project.url
  if (!url) {
    document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' })
    return
  }
  if (/^https?:\/\//.test(url)) {
    window.open(url, '_blank', 'noopener,noreferrer')
  } else {
    // Internal path — navigate so NPM routes to the sub-project
    window.location.assign(url)
  }
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

/* ─── Message bubbles ───────────────────────────────────── */
.chat-bubble {
  position: relative;
  box-shadow: 0 2px 8px oklch(0 0 0 / 0.12);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.chat-bubble:hover {
  box-shadow: 0 4px 14px oklch(0 0 0 / 0.18);
}

.chat-bubble-user {
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));
  box-shadow: 0 4px 14px oklch(0.55 0.20 290 / 0.25);
}

.chat-bubble-assistant-dark {
  background: linear-gradient(180deg, oklch(0.22 0.02 250), oklch(0.19 0.02 250));
  color: oklch(0.95 0 0 / 0.92);
  border: 1px solid oklch(1 0 0 / 0.06);
}

.chat-bubble-assistant-light {
  background: linear-gradient(180deg, oklch(0.98 0.005 250), oklch(0.96 0.005 250));
  color: oklch(0.28 0.02 250);
  border: 1px solid oklch(0 0 0 / 0.05);
}

.chat-avatar {
  box-shadow: 0 2px 10px oklch(0.55 0.20 290 / 0.35);
}

/* ─── Project chips (clickable project references) ──────── */
.chat-project-chip {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 1px 4px oklch(0 0 0 / 0.08);
}

.chat-project-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px oklch(0.55 0.20 290 / 0.2);
}

.chat-project-chip:active {
  transform: translateY(0);
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

/* ─── Paragraphs ───────────────────────────────────────── */
.chat-paragraph {
  margin: 0;
}
.chat-paragraph + .chat-paragraph,
.chat-paragraph + .chat-list,
.chat-list + .chat-paragraph,
.chat-paragraph + .chat-heading,
.chat-heading + .chat-paragraph {
  margin-top: 0.55rem;
}

/* ─── Headings ─────────────────────────────────────────── */
.chat-heading {
  font-weight: 700;
  line-height: 1.25;
  margin: 0.6rem 0 0.3rem 0;
  background: linear-gradient(135deg, var(--color-brand-400), var(--color-accent-400));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.chat-heading-md { font-size: 0.95rem; }
.chat-heading-sm { font-size: 0.88rem; }

/* ─── Strong (bold) ────────────────────────────────────── */
.chat-strong {
  font-weight: 600;
  color: inherit;
}

/* ─── Markdown links as pills ──────────────────────────── */
.chat-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.12rem 0.55rem;
  margin: 0 0.1rem;
  border-radius: 9999px;
  font-weight: 600;
  text-decoration: none;
  background: linear-gradient(135deg,
    oklch(0.55 0.20 250 / 0.18),
    oklch(0.55 0.20 290 / 0.18));
  color: var(--color-brand-300);
  border: 1px solid oklch(0.55 0.20 270 / 0.35);
  transition: all 0.18s ease;
  cursor: pointer;
}

.chat-link:hover {
  background: linear-gradient(135deg,
    oklch(0.55 0.20 250 / 0.30),
    oklch(0.55 0.20 290 / 0.30));
  border-color: oklch(0.60 0.22 270 / 0.65);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px oklch(0.55 0.20 270 / 0.25);
}

.light .chat-link {
  color: var(--color-brand-600);
  background: linear-gradient(135deg,
    oklch(0.55 0.20 250 / 0.10),
    oklch(0.55 0.20 290 / 0.10));
}

.chat-link-icon {
  width: 0.85em;
  height: 0.85em;
  opacity: 0.7;
  flex-shrink: 0;
}

.chat-link:hover .chat-link-icon {
  opacity: 1;
}

/* Bubbles contain block-level elements — tighten last-child margins */
.chat-bubble > *:first-child { margin-top: 0 !important; }
.chat-bubble > *:last-child  { margin-bottom: 0 !important; }
</style>
