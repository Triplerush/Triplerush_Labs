<template>
  <div class="constellation-detail" role="dialog" aria-modal="true" :aria-labelledby="titleId" @keydown.esc="$emit('close')">
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
    </article>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  node: { type: Object, required: true },
  reducedMotion: { type: Boolean, default: false },
})

defineEmits(['close'])

const panelRef = ref(null)
const titleId = `constellation-detail-${props.node.id}`

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

onMounted(async () => {
  await nextTick()
  panelRef.value?.focus()

  if (!props.reducedMotion) {
    gsap.fromTo(panelRef.value, { opacity: 0, scale: 0.96, y: 18 }, { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: 'power3.out' })
  }
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
  width: 40px;
  height: 40px;
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

@media (max-width: 760px) {
  .constellation-detail {
    align-items: end;
    padding: 10px;
  }

  .constellation-detail__panel {
    width: 100%;
    max-height: calc(100dvh - 20px);
    padding: 20px;
    border-radius: 18px 18px 10px 10px;
  }

  .constellation-detail__header,
  .constellation-detail__metadata,
  .constellation-detail__contact {
    grid-template-columns: 1fr;
  }
}
</style>
