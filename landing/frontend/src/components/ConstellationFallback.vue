<template>
  <ul ref="fallbackRef" class="constellation-fallback" aria-label="Resultados semánticos del portfolio">
    <li
      v-for="(node, index) in nodes"
      :key="node.id"
      class="constellation-fallback__entry"
    >
      <button
        type="button"
        class="constellation-fallback__item"
        :class="{
          'constellation-fallback__item--central': node.is_central,
          'constellation-fallback__item--top': isTopResult(node),
          'constellation-fallback__item--muted': isMutedResult(node),
        }"
        :data-node-id="node.id"
        :aria-label="ariaLabel(node, index)"
        @click="$emit('select', node)"
      >
        <span class="constellation-fallback__rank" aria-hidden="true">
          {{ rankLabel(node, index) }}
        </span>

        <span class="constellation-fallback__content">
          <span class="constellation-fallback__name">{{ node.name }}</span>
          <span class="constellation-fallback__meta">
            {{ metaLabel(node) }}
          </span>
        </span>

        <span v-if="scoreLabel(node)" class="constellation-fallback__score" aria-hidden="true">
          {{ scoreLabel(node) }}
        </span>
      </button>
    </li>
  </ul>
</template>

<script setup>
import { nextTick, onMounted, onUpdated, ref } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  nodes: { type: Array, required: true },
  reducedMotion: { type: Boolean, default: false },
})

defineEmits(['select'])

const fallbackRef = ref(null)

const scoredNodes = () => props.nodes.filter((node) => typeof node.score === 'number' && !node.is_central)

const topNodeIds = () => new Set(scoredNodes().slice(0, 3).map((node) => node.id))

const isTopResult = (node) => topNodeIds().has(node.id)

const isMutedResult = (node) => {
  if (node.is_central || typeof node.score !== 'number') return false
  return !isTopResult(node) && node.score < 0.45
}

const scoreLabel = (node) => typeof node.score === 'number' ? node.score.toFixed(2) : ''

const rankLabel = (node, index) => {
  if (node.is_central) return 'FC'
  if (typeof node.score !== 'number') return String(index + 1).padStart(2, '0')
  const rank = scoredNodes().findIndex((candidate) => candidate.id === node.id) + 1
  return rank > 0 ? String(rank).padStart(2, '0') : String(index + 1).padStart(2, '0')
}

const typeLabel = (node) => {
  if (node.is_central) return 'Perfil central'
  if (node.type === 'project') return 'Proyecto'
  if (node.type?.includes('education')) return 'Formación'
  return 'Experiencia'
}

const metaLabel = (node) => {
  const score = scoreLabel(node)
  if (!score) return typeLabel(node)
  return `${typeLabel(node)} · Score ${score}`
}

const ariaLabel = (node, index) => {
  const score = scoreLabel(node)
  const rank = node.is_central ? 'Perfil central' : `Resultado ${rankLabel(node, index)}`
  const scoreText = score ? `, score ${score}` : ''
  return `${rank}: ${node.name}${scoreText}. Abrir detalle.`
}

const animateList = async () => {
  if (props.reducedMotion || !fallbackRef.value) return
  await nextTick()
  const items = fallbackRef.value.querySelectorAll('.constellation-fallback__item')
  gsap.fromTo(items, { y: 8 }, { y: 0, duration: 0.24, stagger: 0.025, ease: 'power2.out', clearProps: 'transform' })
}

onMounted(animateList)
onUpdated(animateList)
</script>

<style scoped>
.constellation-fallback {
  position: relative;
  z-index: 2;
  display: grid;
  gap: 10px;
  width: min(100%, 680px);
  justify-self: center;
  margin-top: 18px;
  margin-bottom: 0;
  padding-left: 0;
  padding-bottom: 18px;
  list-style: none;
}

.constellation-fallback__entry {
  min-width: 0;
}

.constellation-fallback__item {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  min-height: 74px;
  width: 100%;
  padding: 12px;
  border: 1px solid oklch(1 0 0 / 0.10);
  border-radius: 8px;
  background: oklch(0.16 0.02 250 / 0.72);
  color: oklch(0.94 0.01 250);
  text-align: left;
  cursor: pointer;
  backdrop-filter: blur(12px);
}

.constellation-fallback__item--top {
  border-color: oklch(0.65 0.20 250 / 0.36);
  box-shadow: 0 0 28px oklch(0.65 0.20 250 / 0.18);
}

.constellation-fallback__item--central {
  border-color: oklch(1 0 0 / 0.16);
  background:
    radial-gradient(circle at 20% 20%, oklch(0.65 0.15 250 / 0.26), transparent 38%),
    oklch(0.17 0.02 250 / 0.80);
}

.constellation-fallback__item--muted {
  opacity: 0.68;
}

.constellation-fallback__item:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 2px;
}

.constellation-fallback__rank {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));
  color: white;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 900;
}

.constellation-fallback__content {
  display: grid;
  min-width: 0;
  gap: 5px;
}

.constellation-fallback__name {
  overflow-wrap: anywhere;
  font-size: 15px;
  font-weight: 850;
  line-height: 1.2;
}

.constellation-fallback__meta {
  color: oklch(0.90 0.01 250 / 0.62);
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 1.25;
  text-transform: uppercase;
}

.constellation-fallback__score {
  min-width: 46px;
  padding: 5px 8px;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 999px;
  background: oklch(0.65 0.20 250 / 0.20);
  color: oklch(0.95 0.01 250);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 800;
  text-align: center;
}

@media (prefers-reduced-motion: reduce) {
  .constellation-fallback__item {
    transition: none !important;
  }
}
</style>
