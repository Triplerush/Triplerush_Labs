<template>
  <div class="constellation-detail" role="dialog" aria-modal="true" :aria-labelledby="titleId" @keydown.esc.stop="$emit('close')">
    <div class="constellation-detail__backdrop" @click="$emit('close')"></div>
    <article ref="panelRef" class="constellation-detail__panel" tabindex="-1">
      <header class="constellation-detail__header">
        <div>
          <p class="constellation-detail__eyebrow">{{ eyebrow }}</p>
          <h2 :id="titleId">{{ node.name }}</h2>
        </div>
        <button type="button" class="constellation-detail__close" aria-label="Cerrar detalle" @click="$emit('close')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <p class="constellation-detail__summary">{{ summary }}</p>

      <div v-if="scoreLabel" class="constellation-detail__score">
        Coincidencia semántica <strong>{{ scoreLabel }}</strong>
      </div>

      <dl v-if="metadataEntries.length" class="constellation-detail__metadata" aria-label="Datos principales">
        <template v-for="[key, value] in metadataEntries" :key="key">
          <dt>{{ key }}</dt>
          <dd>{{ value }}</dd>
        </template>
      </dl>

      <section v-if="highlights.length" class="constellation-detail__section">
        <h3>Detalle completo</h3>
        <ul>
          <li v-for="item in highlights" :key="item">{{ item }}</li>
        </ul>
      </section>

      <section v-if="demonstrates.length" class="constellation-detail__section">
        <h3>Demuestra</h3>
        <div class="constellation-detail__stack">
          <span v-for="item in demonstrates" :key="item">{{ item }}</span>
        </div>
      </section>

      <section v-if="stack.length" class="constellation-detail__section">
        <h3>Stack</h3>
        <div class="constellation-detail__stack">
          <span v-for="item in stack" :key="item">{{ item }}</span>
        </div>
      </section>

      <section v-if="contactEntries.length" class="constellation-detail__section">
        <h3>Contacto</h3>
        <dl class="constellation-detail__contact">
          <template v-for="[key, value] in contactEntries" :key="key">
            <dt>{{ key }}</dt>
            <dd>{{ value }}</dd>
          </template>
        </dl>
      </section>

      <a v-if="node.data?.url" class="constellation-detail__link" :href="node.data.url">
        Abrir proyecto
      </a>

      <section class="constellation-detail__chat" aria-labelledby="constellation-detail-chat-title">
        <div class="constellation-detail__chat-header">
          <div>
            <h3 id="constellation-detail-chat-title">Preguntar sobre este nodo</h3>
            <p>El contexto de {{ node.name }} se adjunta a cada mensaje.</p>
          </div>
          <button
            type="button"
            class="constellation-detail__chat-clear"
            :disabled="chatMessages.length === 0 && !chatError"
            @click="clearChat"
          >
            Limpiar
          </button>
        </div>

        <div ref="chatLogRef" class="constellation-detail__chat-log" role="log" aria-live="polite" aria-label="Conversación contextual">
          <p v-if="chatMessages.length === 0" class="constellation-detail__chat-empty">
            Haz una pregunta concreta sobre relevancia, stack, experiencia o cómo se conecta con tu búsqueda.
          </p>

          <div
            v-for="(message, index) in chatMessages"
            :key="`${message.role}-${index}`"
            class="constellation-detail__chat-message"
            :class="`constellation-detail__chat-message--${message.role}`"
          >
            <span class="constellation-detail__chat-role">{{ message.role === 'user' ? 'Tú' : 'AI' }}</span>
            <p>{{ message.content || '...' }}</p>
          </div>

          <div v-if="isChatStreaming" class="constellation-detail__chat-thinking" aria-label="Generando respuesta">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <p v-if="chatError" class="constellation-detail__chat-error" role="alert">{{ chatError }}</p>

        <form class="constellation-detail__chat-form" @submit.prevent="submitChat">
          <label class="sr-only" :for="chatInputId">Pregunta contextual</label>
          <textarea
            :id="chatInputId"
            ref="chatInputRef"
            v-model="chatInput"
            rows="2"
            maxlength="500"
            :disabled="isChatStreaming"
            placeholder="Ej. ¿Por qué este proyecto es relevante para RAG en producción?"
            @keydown="handleChatKeydown"
          ></textarea>
          <button type="submit" :disabled="!chatInput.trim() || isChatStreaming">
            Enviar
          </button>
        </form>
      </section>
    </article>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  node: { type: Object, required: true },
  reducedMotion: { type: Boolean, default: false },
})

defineEmits(['close'])

const panelRef = ref(null)
const chatLogRef = ref(null)
const chatInputRef = ref(null)
const chatInput = ref('')
const chatMessages = ref([])
const isChatStreaming = ref(false)
const chatError = ref('')
const titleId = computed(() => `constellation-detail-${props.node.id}`)
const chatInputId = computed(() => `constellation-detail-chat-${props.node.id}`)
let abortController = null
let chatRequestId = 0

const eyebrow = computed(() => {
  if (props.node.is_central) return 'Perfil central'
  if (props.node.type === 'project') return 'Proyecto'
  if (props.node.type?.includes('education')) return 'Formación'
  return 'Experiencia'
})

const summary = computed(() => props.node.data?.summary || props.node.data?.description || 'Detalle de la constelación semántica.')
const highlights = computed(() => props.node.data?.highlights || [])
const stack = computed(() => props.node.data?.stack || [])
const demonstrates = computed(() => props.node.data?.demonstrates || [])
const scoreLabel = computed(() => typeof props.node.score === 'number' ? props.node.score.toFixed(2) : '')
const contactEntries = computed(() => Object.entries(props.node.data?.contact || {}))

const nodeContext = computed(() => {
  const data = props.node.data || {}
  const context = [
    `Nombre: ${props.node.name}`,
    `Tipo: ${eyebrow.value}`,
    props.node.category ? `Categoria: ${props.node.category}` : '',
    typeof props.node.score === 'number' ? `Score semantico: ${props.node.score.toFixed(2)}` : '',
    data.summary || data.description ? `Resumen: ${data.summary || data.description}` : '',
    data.role ? `Rol: ${data.role}` : '',
    data.company ? `Empresa: ${data.company}` : '',
    data.period ? `Periodo: ${data.period}` : '',
    data.status ? `Estado: ${data.status}` : '',
    highlights.value.length ? `Highlights: ${highlights.value.join('; ')}` : '',
    demonstrates.value.length ? `Demuestra: ${demonstrates.value.join(', ')}` : '',
    stack.value.length ? `Stack: ${stack.value.join(', ')}` : '',
    data.url ? `URL: ${data.url}` : '',
  ].filter(Boolean)

  return context.join('\n')
})

const metadataEntries = computed(() => {
  const data = props.node.data || {}
  const entries = []

  if (props.node.type) entries.push(['Tipo', eyebrow.value])
  if (props.node.category) entries.push(['Categoría', props.node.category])
  if (data.role) entries.push(['Rol', data.role])
  if (data.company) entries.push(['Empresa', data.company])
  if (data.period) entries.push(['Periodo', data.period])
  if (data.status) entries.push(['Estado', data.status.toUpperCase()])
  if (data.location) entries.push(['Ubicación', data.location])

  return entries
})

const scrollChatToBottom = () => {
  nextTick(() => {
    if (!chatLogRef.value) return
    chatLogRef.value.scrollTop = chatLogRef.value.scrollHeight
  })
}

const handleChatKeydown = (event) => {
  if (event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  submitChat()
}

const clearChat = () => {
  chatRequestId += 1
  abortController?.abort()
  abortController = null
  chatInput.value = ''
  chatMessages.value = []
  isChatStreaming.value = false
  chatError.value = ''
}

const buildNodeContextMessage = () => {
  return [
    'Contexto del nodo seleccionado en la constelación del portfolio:',
    nodeContext.value,
    'Usa este contexto para responder las siguientes preguntas. Si falta información, dilo brevemente y no inventes datos.',
  ].join('\n')
}

const submitChat = async () => {
  const visibleMessage = chatInput.value.trim()
  if (!visibleMessage || isChatStreaming.value) return

  chatInput.value = ''
  chatError.value = ''
  chatMessages.value.push({ role: 'user', content: visibleMessage })

  const visibleHistory = chatMessages.value
    .slice(-9, -1)
    .map((message) => ({ role: message.role, content: message.content }))

  const history = [
    ...visibleHistory.slice(-4),
    { role: 'user', content: buildNodeContextMessage() },
    { role: 'assistant', content: `Entendido. Responderé sobre ${props.node.name} usando ese contexto.` },
  ]

  const assistantIndex = chatMessages.value.length
  chatMessages.value.push({ role: 'assistant', content: '' })
  isChatStreaming.value = true
  scrollChatToBottom()
  let requestId = 0

  try {
    abortController?.abort()
    requestId = chatRequestId + 1
    chatRequestId = requestId
    abortController = new AbortController()

    const response = await fetch('/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: visibleMessage, history }),
      signal: abortController.signal,
    })

    if (requestId !== chatRequestId) return

    if (response.status === 429) {
      chatMessages.value.splice(assistantIndex, 1)
      chatError.value = 'Demasiados mensajes seguidos. Espera un momento e intenta de nuevo.'
      return
    }

    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      if (requestId !== chatRequestId) return

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6).trim()
        if (!data) continue

        try {
          const event = JSON.parse(data)
          if (event.type === 'token') {
            chatMessages.value[assistantIndex].content += event.content
            scrollChatToBottom()
          } else if (event.type === 'error') {
            chatError.value = event.message || 'Error al generar la respuesta.'
          }
        } catch {
          // Ignore malformed SSE fragments.
        }
      }
    }

    if (requestId !== chatRequestId) return

    if (!chatMessages.value[assistantIndex]?.content) {
      chatMessages.value[assistantIndex].content = 'No pude generar una respuesta para este nodo.'
    }
  } catch (error) {
    if (error.name === 'AbortError') return
    if (assistantIndex >= chatMessages.value.length) return
    if (chatMessages.value[assistantIndex]?.content === '') {
      chatMessages.value.splice(assistantIndex, 1)
    }
    chatError.value = 'No pude conectar con el chat contextual.'
  } finally {
    if (requestId === chatRequestId) {
      isChatStreaming.value = false
      abortController = null
      scrollChatToBottom()
    }
  }
}

watch(() => props.node.id, () => {
  clearChat()
})

watch(chatMessages, scrollChatToBottom, { deep: true })

onMounted(async () => {
  await nextTick()
  panelRef.value?.focus()

  if (!props.reducedMotion) {
    gsap.fromTo(panelRef.value, { opacity: 0, scale: 0.96, y: 18 }, { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: 'power3.out' })
  }
})

onBeforeUnmount(() => {
  chatRequestId += 1
  abortController?.abort()
})
</script>

<style scoped>
.constellation-detail {
  position: fixed;
  inset: 0;
  z-index: 10020;
  display: grid;
  place-items: center;
  padding: 18px;
}

.constellation-detail__backdrop {
  position: absolute;
  inset: 0;
  background: oklch(0.05 0.01 250 / 0.72);
  backdrop-filter: blur(10px);
}

.constellation-detail__panel {
  position: relative;
  width: min(920px, 100%);
  max-height: calc(100dvh - 36px);
  overflow: auto;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 18px;
  background: oklch(0.13 0.02 250 / 0.94);
  box-shadow: 0 30px 120px oklch(0 0 0 / 0.46);
  color: oklch(0.94 0.01 250);
  padding: 26px;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.constellation-detail__panel:focus {
  outline: none;
}

.constellation-detail__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.constellation-detail__eyebrow {
  margin: 0 0 6px;
  color: var(--color-brand-300);
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
}

.constellation-detail h2 {
  margin: 0;
  font-size: clamp(24px, 4vw, 38px);
  line-height: 1.04;
  font-weight: 900;
}

.constellation-detail__close {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 12px;
  background: oklch(1 0 0 / 0.04);
  color: white;
  cursor: pointer;
}

.constellation-detail__close svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 2;
}

.constellation-detail__close:focus-visible,
.constellation-detail__link:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 2px;
}

.constellation-detail__summary {
  margin: 22px 0 0;
  color: oklch(0.88 0.01 250 / 0.82);
  font-size: 15px;
  line-height: 1.7;
}

.constellation-detail__score {
  width: fit-content;
  margin-top: 18px;
  padding: 8px 12px;
  border: 1px solid oklch(1 0 0 / 0.10);
  border-radius: 999px;
  background: oklch(0.65 0.20 250 / 0.18);
  font-size: 13px;
}

.constellation-detail__metadata {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 8px 14px;
  margin: 20px 0 0;
  padding: 14px;
  border: 1px solid oklch(1 0 0 / 0.08);
  border-radius: 14px;
  background: oklch(1 0 0 / 0.04);
  font-size: 13px;
}

.constellation-detail__metadata dt {
  color: oklch(0.90 0.01 250 / 0.55);
  font-weight: 800;
}

.constellation-detail__metadata dd {
  margin: 0;
  color: oklch(0.92 0.01 250 / 0.86);
}

.constellation-detail__section {
  margin-top: 24px;
}

.constellation-detail__section h3 {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  color: oklch(0.90 0.01 250 / 0.72);
}

.constellation-detail__section ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 20px;
  color: oklch(0.88 0.01 250 / 0.82);
  line-height: 1.55;
}

.constellation-detail__stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.constellation-detail__stack span {
  padding: 5px 9px;
  border: 1px solid oklch(1 0 0 / 0.10);
  border-radius: 999px;
  background: oklch(1 0 0 / 0.05);
  font-family: var(--font-mono);
  font-size: 11px;
}

.constellation-detail__contact {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 8px 14px;
  margin: 0;
  font-size: 14px;
}

.constellation-detail__contact dt {
  color: oklch(0.90 0.01 250 / 0.55);
}

.constellation-detail__contact dd {
  margin: 0;
}

.constellation-detail__link {
  display: inline-flex;
  margin-top: 26px;
  padding: 10px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));
  color: white;
  font-weight: 800;
  text-decoration: none;
}

.constellation-detail__chat {
  display: grid;
  gap: 12px;
  margin-top: 26px;
  padding: 16px;
  border: 1px solid oklch(1 0 0 / 0.10);
  border-radius: 16px;
  background: oklch(1 0 0 / 0.035);
}

.constellation-detail__chat-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.constellation-detail__chat h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 900;
  text-transform: uppercase;
  color: oklch(0.90 0.01 250 / 0.78);
}

.constellation-detail__chat-header p {
  margin: 5px 0 0;
  color: oklch(0.88 0.01 250 / 0.58);
  font-size: 12px;
  line-height: 1.45;
}

.constellation-detail__chat-clear {
  min-height: 34px;
  padding: 0 10px;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 10px;
  background: oklch(1 0 0 / 0.04);
  color: oklch(0.92 0.01 250);
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.constellation-detail__chat-clear:disabled {
  cursor: not-allowed;
  opacity: 0.42;
}

.constellation-detail__chat-log {
  display: grid;
  gap: 10px;
  min-height: 132px;
  max-height: 260px;
  overflow: auto;
  padding: 12px;
  border: 1px solid oklch(1 0 0 / 0.08);
  border-radius: 14px;
  background: oklch(0.08 0.015 250 / 0.54);
  scrollbar-gutter: stable;
}

.constellation-detail__chat-empty {
  align-self: center;
  margin: 0;
  color: oklch(0.88 0.01 250 / 0.52);
  font-size: 13px;
  line-height: 1.55;
}

.constellation-detail__chat-message {
  display: grid;
  gap: 4px;
  max-width: min(78%, 560px);
}

.constellation-detail__chat-message--user {
  justify-self: end;
}

.constellation-detail__chat-role {
  color: oklch(0.88 0.01 250 / 0.50);
  font-family: var(--font-mono);
  font-size: 10px;
  text-transform: uppercase;
}

.constellation-detail__chat-message--user .constellation-detail__chat-role {
  justify-self: end;
}

.constellation-detail__chat-message p {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid oklch(1 0 0 / 0.08);
  border-radius: 14px;
  background: oklch(1 0 0 / 0.06);
  color: oklch(0.90 0.01 250 / 0.88);
  font-size: 13px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.constellation-detail__chat-message--user p {
  border-color: oklch(0.55 0.20 250 / 0.34);
  background: oklch(0.55 0.20 250 / 0.22);
  color: white;
}

.constellation-detail__chat-thinking {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  padding: 10px 12px;
  border-radius: 14px;
  background: oklch(1 0 0 / 0.06);
}

.constellation-detail__chat-thinking span {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--color-brand-300);
  animation: constellation-detail-thinking 1100ms ease-in-out infinite;
  opacity: 0.52;
}

.constellation-detail__chat-thinking span:nth-child(2) {
  animation-delay: 140ms;
}

.constellation-detail__chat-thinking span:nth-child(3) {
  animation-delay: 280ms;
}

.constellation-detail__chat-error {
  margin: 0;
  padding: 9px 11px;
  border: 1px solid oklch(0.65 0.20 25 / 0.24);
  border-radius: 12px;
  background: oklch(0.30 0.12 25 / 0.20);
  color: oklch(0.88 0.08 35);
  font-size: 12px;
}

.constellation-detail__chat-form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: end;
}

.constellation-detail__chat-form textarea {
  width: 100%;
  min-height: 50px;
  max-height: 120px;
  resize: vertical;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 12px;
  background: oklch(0.08 0.015 250 / 0.62);
  color: oklch(0.94 0.01 250);
  font: inherit;
  font-size: 13px;
  line-height: 1.45;
  padding: 10px 12px;
  outline: none;
}

.constellation-detail__chat-form textarea::placeholder {
  color: oklch(0.88 0.01 250 / 0.38);
}

.constellation-detail__chat-form button {
  min-height: 50px;
  padding: 0 14px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));
  color: white;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
}

.constellation-detail__chat-form button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.constellation-detail__chat-clear:focus-visible,
.constellation-detail__chat-form textarea:focus-visible,
.constellation-detail__chat-form button:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 2px;
}

@keyframes constellation-detail-thinking {
  0%, 70%, 100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  35% {
    transform: translateY(-5px);
    opacity: 1;
  }
}

@media (max-width: 767px) {
  .constellation-detail {
    align-items: end;
    padding: 12px;
  }

  .constellation-detail__panel {
    width: 100%;
    max-height: min(82dvh, calc(100dvh - 24px));
    padding: 20px;
    border-radius: 18px 18px 10px 10px;
  }

  .constellation-detail__header,
  .constellation-detail__metadata,
  .constellation-detail__contact {
    grid-template-columns: 1fr;
  }

  .constellation-detail__chat-header,
  .constellation-detail__chat-form {
    grid-template-columns: 1fr;
  }

  .constellation-detail__chat-header {
    display: grid;
  }

  .constellation-detail__chat-clear,
  .constellation-detail__chat-form button {
    width: 100%;
  }

  .constellation-detail__chat-message {
    max-width: 92%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-detail__chat-thinking span {
    animation: none;
  }
}
</style>
