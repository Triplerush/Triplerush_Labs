<template>
  <div class="detail" role="dialog" aria-modal="false" :aria-labelledby="titleId" @keydown.esc.stop="$emit('close')">
    <div class="detail__backdrop" @click="$emit('close')"></div>
    <article ref="panelRef" class="detail__panel" tabindex="-1">
      <header class="detail__header">
        <div class="detail__title-block">
          <p class="detail__eyebrow">{{ eyebrow }}</p>
          <h2 :id="titleId" class="detail__title">{{ node.name }}</h2>
          <p v-if="subtitleLine" class="detail__subtitle">{{ subtitleLine }}</p>
        </div>
        <button
          type="button"
          class="detail__close"
          aria-label="Cerrar detalle"
          @click="$emit('close')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <div class="detail__body">
        <a
          v-if="isProject && node.data?.url"
          class="detail__cta"
          :href="node.data.url"
          target="_self"
        >
          <span>Abrir demo</span>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M7 17L17 7M9 7h8v8" />
          </svg>
        </a>

        <p v-if="summary" class="detail__summary">{{ summary }}</p>

        <div v-if="scoreLabel || statusBadge" class="detail__badges">
          <span v-if="scoreLabel" class="detail__badge detail__badge--score">
            Coincidencia <strong>{{ scoreLabel }}</strong>
          </span>
          <span v-if="statusBadge" class="detail__badge" :class="`detail__badge--${statusBadge.tone}`">
            {{ statusBadge.label }}
          </span>
        </div>

        <section v-if="highlights.length" class="detail__section">
          <h3>{{ highlightsTitle }}</h3>
          <ul>
            <li v-for="item in highlights" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section v-if="demonstrates.length" class="detail__section">
          <h3>Demuestra</h3>
          <div class="detail__chips">
            <span v-for="item in demonstrates" :key="item" class="detail__chip">{{ item }}</span>
          </div>
        </section>

        <section v-if="stack.length" class="detail__section">
          <h3>Stack</h3>
          <div class="detail__chips">
            <span v-for="item in stack" :key="item" class="detail__chip detail__chip--mono">{{ item }}</span>
          </div>
        </section>

        <section v-if="languages.length" class="detail__section">
          <h3>Idiomas</h3>
          <div class="detail__chips">
            <span v-for="item in languages" :key="item" class="detail__chip">{{ item }}</span>
          </div>
        </section>

        <section v-if="roadmap.length" class="detail__section">
          <h3>Roadmap de carrera</h3>
          <ul class="detail__roadmap">
            <li v-for="item in roadmap" :key="item">{{ item }}</li>
          </ul>
        </section>

        <section v-if="contactLinks.length" class="detail__section">
          <h3>Contacto</h3>
          <ul class="detail__contact">
            <li v-for="entry in contactLinks" :key="entry.key">
              <span class="detail__contact-key">{{ entry.label }}</span>
              <a v-if="entry.href" :href="entry.href">{{ entry.value }}</a>
              <span v-else>{{ entry.value }}</span>
            </li>
          </ul>
        </section>

        <section v-if="relatedNodes.length" class="detail__section">
          <h3>Nodos conectados</h3>
          <div class="detail__related">
            <button
              v-for="related in relatedNodes"
              :key="related.id"
              type="button"
              class="detail__related-chip"
              @click="$emit('navigate', related.id)"
            >
              <span class="detail__related-type">{{ relatedTypeLabel(related) }}</span>
              <span class="detail__related-name">{{ related.name }}</span>
            </button>
          </div>
        </section>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  node: { type: Object, required: true },
  relatedNodes: { type: Array, default: () => [] },
  reducedMotion: { type: Boolean, default: false },
})

defineEmits(['close', 'navigate'])

const panelRef = ref(null)
const titleId = computed(() => `detail-${props.node.id}`)

const isProject = computed(() => props.node.type === 'project')

const eyebrow = computed(() => {
  if (props.node.is_central) return 'Perfil central'
  switch (props.node.type) {
    case 'project': return 'Proyecto'
    case 'experience': return 'Experiencia'
    case 'education': return 'Formación'
    case 'skill': return 'Skills'
    default: return 'Nodo'
  }
})

const subtitleLine = computed(() => {
  const data = props.node.data || {}
  const parts = []
  if (props.node.is_central && data.role) parts.push(data.role)
  if (data.company) parts.push(data.company)
  if (data.institution && !parts.length) parts.push(data.institution)
  if (data.period) parts.push(data.period)
  if (data.location && parts.length < 3) parts.push(data.location)
  return parts.join(' · ')
})

const summary = computed(() => props.node.data?.summary || props.node.data?.description || '')
const highlights = computed(() => props.node.data?.highlights || [])
const stack = computed(() => props.node.data?.stack || [])
const demonstrates = computed(() => props.node.data?.demonstrates || [])
const languages = computed(() => props.node.data?.languages || [])
const roadmap = computed(() => props.node.data?.roadmap || [])
const scoreLabel = computed(() => typeof props.node.score === 'number' ? props.node.score.toFixed(2) : '')

const highlightsTitle = computed(() => {
  switch (props.node.type) {
    case 'experience': return 'Trayectoria'
    case 'project': return 'Highlights'
    case 'education': return 'Formación'
    case 'skill': return 'Capacidades'
    default: return 'Highlights'
  }
})

const statusBadge = computed(() => {
  const status = props.node.data?.status
  if (!status) return null
  if (status === 'live') return { label: 'Live', tone: 'live' }
  if (status === 'wip') return { label: 'WIP', tone: 'wip' }
  return { label: status, tone: 'neutral' }
})

const contactLinks = computed(() => {
  const contact = props.node.data?.contact
  if (!contact) return []
  const entries = []
  if (contact.email) entries.push({ key: 'email', label: 'Email', value: contact.email, href: `mailto:${contact.email}` })
  if (contact.phone) entries.push({ key: 'phone', label: 'Teléfono', value: contact.phone, href: `tel:${contact.phone.replace(/\s+/g, '')}` })
  if (contact.linkedin) entries.push({ key: 'linkedin', label: 'LinkedIn', value: contact.linkedin, href: `https://${contact.linkedin.replace(/^https?:\/\//, '')}` })
  if (contact.github) entries.push({ key: 'github', label: 'GitHub', value: contact.github, href: `https://${contact.github.replace(/^https?:\/\//, '')}` })
  if (contact.location) entries.push({ key: 'location', label: 'Ubicación', value: contact.location, href: '' })
  return entries
})

const relatedTypeLabel = (node) => {
  if (node.is_central) return 'Persona'
  switch (node.type) {
    case 'project': return 'Proyecto'
    case 'experience': return 'Experiencia'
    case 'education': return 'Formación'
    case 'skill': return 'Skills'
    default: return 'Nodo'
  }
}

onMounted(async () => {
  await nextTick()
  panelRef.value?.focus()

  if (!props.reducedMotion) {
    gsap.fromTo(
      panelRef.value,
      { opacity: 0, x: 24 },
      { opacity: 1, x: 0, duration: 0.36, ease: 'power3.out' },
    )
  }
})
</script>

<style scoped>
.detail {
  position: fixed;
  inset: 0;
  z-index: 10020;
  pointer-events: none;
}

.detail__backdrop {
  position: absolute;
  inset: 0;
  background: transparent;
  pointer-events: auto;
}

.detail__panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(460px, 100%);
  border-left: 1px solid var(--color-border);
  background: rgba(8, 9, 11, 0.92);
  backdrop-filter: blur(18px);
  color: var(--color-text);
  pointer-events: auto;
  overflow: auto;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.detail__panel:focus {
  outline: none;
}

.detail__header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 16px;
  border-bottom: 1px solid var(--color-border);
  background: rgba(8, 9, 11, 0.92);
  backdrop-filter: blur(18px);
}

.detail__title-block {
  min-width: 0;
}

.detail__eyebrow {
  margin: 0 0 8px;
  color: var(--color-accent);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.detail__title {
  margin: 0;
  font-size: clamp(20px, 3vw, 28px);
  line-height: 1.15;
  font-weight: 600;
  letter-spacing: -0.015em;
}

.detail__subtitle {
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 12px;
  letter-spacing: 0.02em;
}

.detail__close {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  transition: border-color 200ms var(--constellation-ease-out);
  flex-shrink: 0;
}

.detail__close:hover {
  border-color: var(--color-accent);
}

.detail__close:focus-visible {
  outline: 1px solid var(--color-accent);
  outline-offset: 2px;
}

.detail__close svg {
  width: 14px;
  height: 14px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 2;
}

.detail__body {
  padding: 20px 24px 32px;
}

.detail__cta {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  margin-bottom: 22px;
  padding: 14px 18px;
  border: 1px solid var(--color-accent);
  border-radius: 4px;
  background: rgba(0, 229, 255, 0.06);
  color: var(--color-accent);
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 200ms ease;
}

.detail__cta:hover {
  background: rgba(0, 229, 255, 0.14);
}

.detail__cta svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-width: 1.6;
}

.detail__summary {
  margin: 0 0 18px;
  color: rgba(245, 247, 250, 0.84);
  font-size: 14px;
  line-height: 1.65;
}

.detail__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.detail__badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--color-text);
}

.detail__badge--score {
  border-color: var(--color-border-strong);
  background: rgba(0, 229, 255, 0.08);
  color: var(--color-accent);
}

.detail__badge--live {
  border-color: rgba(64, 220, 130, 0.40);
  background: rgba(64, 220, 130, 0.06);
  color: rgba(120, 232, 165, 1);
}

.detail__badge--wip {
  border-color: rgba(255, 196, 80, 0.40);
  background: rgba(255, 196, 80, 0.06);
  color: rgba(255, 220, 140, 1);
}

.detail__section {
  margin-top: 22px;
}

.detail__section h3 {
  margin: 0 0 10px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.detail__section ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 18px;
  color: rgba(245, 247, 250, 0.86);
  line-height: 1.55;
  font-size: 13px;
}

.detail__section ul li::marker {
  color: var(--color-accent);
}

.detail__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail__chip {
  padding: 4px 9px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: transparent;
  color: var(--color-text);
  font-size: 11px;
}

.detail__chip--mono {
  font-size: 11px;
  letter-spacing: 0.02em;
  color: var(--color-muted);
}

.detail__roadmap {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.detail__roadmap li {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: transparent;
  color: rgba(245, 247, 250, 0.86);
  font-size: 12px;
  line-height: 1.5;
}

.detail__contact {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.detail__contact li {
  display: grid;
  grid-template-columns: 90px 1fr;
  align-items: baseline;
  gap: 12px;
  font-size: 13px;
}

.detail__contact-key {
  color: var(--color-muted);
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.detail__contact a {
  color: var(--color-accent);
  text-decoration: none;
  border-bottom: 1px dashed transparent;
  transition: border-color 200ms ease;
  word-break: break-word;
}

.detail__contact a:hover,
.detail__contact a:focus-visible {
  border-bottom-color: var(--color-accent);
}

.detail__related {
  display: grid;
  gap: 6px;
}

.detail__related-chip {
  display: grid;
  gap: 3px;
  padding: 9px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: transparent;
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
  transition: border-color 200ms var(--constellation-ease-out),
              background 200ms var(--constellation-ease-out);
}

.detail__related-chip:hover,
.detail__related-chip:focus-visible {
  border-color: var(--color-accent);
  background: rgba(0, 229, 255, 0.04);
  outline: none;
}

.detail__related-type {
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.detail__related-name {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.2;
}

@media (max-width: 767px) {
  .detail__panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--color-border);
    top: auto;
    height: 80dvh;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
  }

  .detail__contact li {
    grid-template-columns: 1fr;
  }
}
</style>
