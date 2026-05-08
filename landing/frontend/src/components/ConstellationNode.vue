<template>
  <button
    ref="nodeRef"
    type="button"
    class="constellation-node"
    :class="[
      `constellation-node--${node.type || 'project'}`,
      {
        'constellation-node--central': node.is_central,
        'constellation-node--dragging': isDragging,
        'constellation-node--related': related,
        'constellation-node--muted': muted,
        'constellation-node--top': topRank === 1,
        'constellation-node--podium': topRank === 2 || topRank === 3,
      },
    ]"
    :style="nodeStyle"
    :data-node-id="node.id"
    :aria-label="ariaLabel"
    @click="handleClick"
    @keydown.enter.prevent="emit('select', node)"
    @keydown.space.prevent="emit('select', node)"
    @pointerenter="emit('node-hover', node)"
    @pointerleave="emit('node-leave', node)"
    @focus="emit('node-hover', node)"
    @blur="emit('node-leave', node)"
    @pointerdown="handlePointerDown"
    @pointermove="handlePointerMove"
    @pointerup="handlePointerUp"
    @pointercancel="handlePointerUp"
  >
    <span class="constellation-node__shape">
      <span class="constellation-node__type" v-if="!node.is_central">{{ typeLabel }}</span>
      <span class="constellation-node__primary">{{ primaryLabel }}</span>
      <span v-if="secondaryLabel" class="constellation-node__secondary">{{ secondaryLabel }}</span>
      <span v-if="showScore" class="constellation-node__score">{{ node.score.toFixed(2) }}</span>
    </span>
  </button>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  node: { type: Object, required: true },
  position: { type: Object, required: true },
  visual: { type: Object, required: true },
  reducedMotion: { type: Boolean, default: false },
  related: { type: Boolean, default: false },
  muted: { type: Boolean, default: false },
  topRank: { type: Number, default: 0 },
})

const emit = defineEmits(['select', 'node-hover', 'node-leave', 'node-drag-start', 'node-drag', 'node-drag-end'])

const nodeRef = ref(null)
const isDragging = ref(false)
const suppressClick = ref(false)
let dragStartPoint = null

const showScore = computed(() => typeof props.node.score === 'number' && !props.node.is_central)

const primaryLabel = computed(() => {
  const data = props.node.data || {}
  if (props.node.is_central) return 'Fernando'
  if (props.node.type === 'experience') return 'Experiencia'
  if (props.node.type === 'education') return 'Formación'
  if (props.node.type === 'skill') return 'Skills'
  if (props.node.type === 'project') {
    return data.name || props.node.name
  }
  return props.node.name
})

const secondaryLabel = computed(() => {
  if (props.node.is_central) return 'Canal'
  if (props.node.type === 'project') {
    const data = props.node.data || {}
    return data.status === 'live' ? 'Live demo' : ''
  }
  return ''
})

const typeLabel = computed(() => {
  switch (props.node.type) {
    case 'experience': return 'Experiencia'
    case 'education': return 'Formación'
    case 'skill': return 'Skills'
    case 'project': return 'Proyecto'
    default: return ''
  }
})

const ariaLabel = computed(() => {
  const score = typeof props.node.score === 'number' ? `, score ${props.node.score.toFixed(2)}` : ''
  return `${props.node.name}${score}. Abrir detalle.`
})

const nodeStyle = computed(() => ({
  left: `${props.position.x}%`,
  top: `${props.position.y}%`,
  '--node-scale': props.visual?.scale ?? 1,
  '--node-opacity': props.visual?.opacity ?? 1,
}))

const handleClick = () => {
  if (suppressClick.value) {
    suppressClick.value = false
    return
  }
  emit('select', props.node)
}

const handlePointerDown = (event) => {
  if (event.button !== 0 || props.reducedMotion || props.node.is_central) return

  dragStartPoint = { x: event.clientX, y: event.clientY }
  isDragging.value = true
  event.currentTarget.setPointerCapture?.(event.pointerId)
  emit('node-drag-start', props.node, event)
}

const handlePointerMove = (event) => {
  if (!isDragging.value) return

  if (dragStartPoint) {
    const distance = Math.hypot(event.clientX - dragStartPoint.x, event.clientY - dragStartPoint.y)
    if (distance > 5) suppressClick.value = true
  }

  emit('node-drag', event)
}

const handlePointerUp = (event) => {
  if (!isDragging.value) return

  isDragging.value = false
  dragStartPoint = null
  event.currentTarget.releasePointerCapture?.(event.pointerId)
  emit('node-drag-end', event)
}
</script>

<style scoped>
.constellation-node {
  position: absolute;
  z-index: 3;
  display: grid;
  width: 104px;
  height: 104px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  opacity: var(--node-opacity, 1);
  transform: translate(-50%, -50%) scale(var(--node-scale, 1));
  transform-origin: center;
  user-select: none;
  transition: opacity 480ms var(--constellation-ease-out),
              transform 480ms var(--constellation-ease-out);
}

@media (prefers-reduced-motion: reduce) {
  .constellation-node {
    transition: none;
  }
}

.constellation-node:focus-visible {
  outline: none;
}

.constellation-node:focus-visible .constellation-node__shape {
  outline: 1px solid var(--color-accent);
  outline-offset: 4px;
}

/* The shape fills the button and centers its labels inside. */
.constellation-node__shape {
  position: relative;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 3px;
  width: 100%;
  height: 100%;
  padding: 14px 12px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  color: var(--color-text);
  text-align: center;
  transition: border-color 240ms var(--constellation-ease-out),
              background-color 240ms var(--constellation-ease-out),
              box-shadow 240ms var(--constellation-ease-out);
}

.constellation-node__type {
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-muted);
  line-height: 1;
}

.constellation-node__primary {
  max-width: 100%;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.18;
  letter-spacing: -0.005em;
  color: inherit;
  word-break: break-word;
  hyphens: auto;
}

.constellation-node__secondary {
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: inherit;
  opacity: 0.7;
  line-height: 1;
}

.constellation-node__score {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 4;
  padding: 1px 6px;
  border: 1px solid var(--color-border-strong);
  border-radius: 3px;
  background: var(--color-bg);
  color: var(--color-accent);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.02em;
  line-height: 1.4;
}

/* ── Type variants — light or contrasting fills ────── */
/* Person: larger button, filled light fill, dark text */
.constellation-node--person {
  width: 124px;
  height: 124px;
}

.constellation-node--person .constellation-node__shape {
  padding: 18px 14px;
  border-color: rgba(255, 255, 255, 0.2);
  background: var(--color-node-core);
  color: #08090B;
  box-shadow: 0 0 32px rgba(0, 229, 255, 0.18);
}

.constellation-node--person .constellation-node__primary {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.constellation-node--person .constellation-node__secondary {
  color: #38393E;
  font-size: 11px;
  letter-spacing: -0.005em;
  text-transform: none;
  font-weight: 500;
  opacity: 0.8;
}

/* Project: cyan-filled — the "live demo" call to action */
.constellation-node--project .constellation-node__shape {
  border-color: var(--color-accent);
  background: var(--color-accent);
  color: #08090B;
  box-shadow: 0 0 26px rgba(0, 229, 255, 0.36);
}

.constellation-node--project .constellation-node__type {
  color: #0A4047;
}

.constellation-node--project .constellation-node__secondary {
  color: #08090B;
  opacity: 0.8;
}

/* Skill: subtle cyan tint, accent text */
.constellation-node--skill .constellation-node__shape {
  border-color: rgba(0, 229, 255, 0.42);
  border-style: dashed;
  background: rgba(0, 229, 255, 0.08);
  color: var(--color-text);
}

.constellation-node--skill .constellation-node__primary {
  color: var(--color-accent);
}

/* Experience: dark filled surface, white text, subtle accent border */
.constellation-node--experience .constellation-node__shape {
  border-color: rgba(255, 255, 255, 0.32);
  background: rgba(255, 255, 255, 0.06);
}

/* Education: dark filled surface with neutral border */
.constellation-node--education .constellation-node__shape {
  border-color: rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.04);
}

/* ── Hover & states ──────────────────────────────── */
.constellation-node:hover .constellation-node__shape {
  border-color: var(--color-accent);
  box-shadow: 0 0 22px rgba(0, 229, 255, 0.28);
}

.constellation-node--related .constellation-node__shape {
  border-color: var(--color-accent);
}

.constellation-node--muted {
  opacity: calc(var(--node-opacity, 1) * 0.34);
}

.constellation-node--dragging {
  z-index: 6;
}

.constellation-node--dragging .constellation-node__shape {
  border-color: var(--color-accent);
  box-shadow: 0 0 36px rgba(0, 229, 255, 0.42);
}

/* Top-ranked search result */
.constellation-node--top .constellation-node__shape {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.18),
              0 0 36px rgba(0, 229, 255, 0.42);
}

.constellation-node--top .constellation-node__shape::after {
  content: '';
  position: absolute;
  inset: -10px;
  border-radius: inherit;
  border: 1px solid rgba(0, 229, 255, 0.55);
  opacity: 0;
  pointer-events: none;
  animation: constellation-node-pulse 2200ms ease-out infinite;
}

.constellation-node--podium .constellation-node__shape {
  border-color: rgba(0, 229, 255, 0.65);
  box-shadow: 0 0 22px rgba(0, 229, 255, 0.22);
}

@keyframes constellation-node-pulse {
  0% { opacity: 0.55; transform: scale(0.9); }
  60%, 100% { opacity: 0; transform: scale(1.4); }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-node,
  .constellation-node__shape {
    animation: none !important;
    transition: none !important;
  }
}
</style>
