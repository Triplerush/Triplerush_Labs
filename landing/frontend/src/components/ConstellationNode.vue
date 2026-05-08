<template>
  <button
    ref="nodeRef"
    type="button"
    class="constellation-node"
    :class="[
      `constellation-node--${node.category || 'backend'}`,
      {
        'constellation-node--central': node.is_central,
        'constellation-node--experience': isExperience,
        'constellation-node--agitated': agitated,
        'constellation-node--dragging': isDragging,
        'constellation-node--pulse': pulseRank > 0 && !reducedMotion,
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
    <span v-if="node.is_central" class="constellation-node__ring" aria-hidden="true"></span>
    <span class="constellation-node__sphere">
      <span class="constellation-node__label">{{ label }}</span>
      <span v-if="node.is_central" class="constellation-node__role">AI Software Engineer</span>
    </span>
    <span v-if="showScore" ref="badgeRef" class="constellation-node__score">
      {{ node.score.toFixed(2) }}
    </span>
  </button>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  node: { type: Object, required: true },
  position: { type: Object, required: true },
  visual: { type: Object, required: true },
  reducedMotion: { type: Boolean, default: false },
  agitated: { type: Boolean, default: false },
  pulseRank: { type: Number, default: 0 },
})

const emit = defineEmits(['select', 'node-hover', 'node-leave', 'node-drag-start', 'node-drag', 'node-drag-end'])

const nodeRef = ref(null)
const badgeRef = ref(null)
const isDragging = ref(false)
const suppressClick = ref(false)
let dragStartPoint = null

const isExperience = computed(() => props.node.type?.includes('experience') || props.node.type?.includes('education'))
const showScore = computed(() => typeof props.node.score === 'number' && !props.node.is_central)
const label = computed(() => props.node.is_central ? 'FC' : props.node.name)

const ariaLabel = computed(() => {
  const score = typeof props.node.score === 'number' ? `, score ${props.node.score.toFixed(2)}` : ''
  return `${props.node.name}${score}. Abrir detalle.`
})

const nodeStyle = computed(() => ({
  left: `${props.position.x}%`,
  top: `${props.position.y}%`,
  '--node-scale': props.visual.scale,
  '--node-opacity': props.visual.opacity,
  '--node-glow': props.visual.glow,
  '--node-color': props.visual.color,
  '--node-pulse-delay': `${Math.max(0, props.pulseRank - 1) * 180}ms`,
}))

const handleClick = () => {
  if (suppressClick.value) {
    suppressClick.value = false
    return
  }
  emit('select', props.node)
}

const handlePointerDown = (event) => {
  if (event.button !== 0 || props.node.is_central || props.reducedMotion) return

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

const applyVisual = () => {
  if (!nodeRef.value) return

  const vars = {
    scale: props.visual.scale,
    opacity: props.visual.opacity,
    boxShadow: props.visual.glow,
    duration: props.reducedMotion ? 0 : 0.8,
    ease: 'power3.out',
  }

  gsap.to(nodeRef.value, vars)

  if (badgeRef.value && !props.reducedMotion) {
    gsap.fromTo(badgeRef.value, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.2, ease: 'power2.out' })
  }
}

onMounted(applyVisual)
watch(() => [props.visual.scale, props.visual.opacity, props.visual.glow, props.node.score], applyVisual)

onBeforeUnmount(() => {
  if (nodeRef.value) gsap.killTweensOf(nodeRef.value)
  if (badgeRef.value) gsap.killTweensOf(badgeRef.value)
})
</script>

<style scoped>
.constellation-node {
  position: absolute;
  z-index: 3;
  width: 80px;
  height: 80px;
  padding: 0;
  border: 0;
  border-radius: 999px;
  color: oklch(0.95 0.01 250);
  cursor: grab;
  opacity: var(--node-opacity);
  transform: translate(-50%, -50%) scale(var(--node-scale));
  transform-origin: center;
  background: transparent;
  box-shadow: var(--node-glow);
  touch-action: none;
  user-select: none;
}

.constellation-node:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 6px;
}

.constellation-node__sphere {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 2px;
  border: 1px solid oklch(1 0 0 / 0.08);
  border-radius: inherit;
  background:
    radial-gradient(circle at 30% 25%, color-mix(in oklch, var(--node-color), white 16%), transparent 32%),
    radial-gradient(circle at 38% 35%, var(--node-color), oklch(0.20 0.04 250) 72%);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.constellation-node__label {
  max-width: 68px;
  padding: 0 5px;
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1.08;
  font-weight: 700;
  text-align: center;
  text-shadow: 0 1px 2px oklch(0 0 0 / 0.75);
}

.constellation-node__role {
  max-width: 86px;
  font-size: 9px;
  line-height: 1;
  opacity: 0.72;
}

.constellation-node__score {
  position: absolute;
  top: -8px;
  right: -10px;
  z-index: 4;
  padding: 2px 7px;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 999px;
  background: var(--color-glow-active, oklch(0.65 0.20 250 / 0.6));
  color: oklch(0.95 0.01 250);
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1.35;
}

.constellation-node--experience {
  width: 72px;
  height: 72px;
}

.constellation-node--experience .constellation-node__sphere {
  border: 2px solid var(--node-color);
  background: oklch(0.17 0.02 250 / 0.45);
}

.constellation-node--central {
  z-index: 5;
  width: 140px;
  height: 140px;
  opacity: 1;
  box-shadow: 0 0 30px oklch(0.55 0.20 250 / 0.5);
}

.constellation-node--agitated {
  animation: constellation-vibration 380ms linear infinite;
}

.constellation-node--dragging {
  z-index: 6;
  opacity: var(--constellation-node-drag-opacity, 1);
  transform: translate(-50%, -50%) scale(calc(var(--node-scale) * var(--constellation-node-drag-scale, 1.08)));
  box-shadow: var(--constellation-node-drag-shadow, 0 0 48px oklch(0.65 0.20 250 / 0.72));
  cursor: grabbing;
}

.constellation-node--pulse::after {
  content: '';
  position: absolute;
  inset: -9px;
  border: 1px solid color-mix(in oklch, var(--node-color), white 18%);
  border-radius: inherit;
  opacity: 0;
  animation: constellation-top-pulse 2400ms ease-out infinite;
  animation-delay: var(--node-pulse-delay);
  pointer-events: none;
}

.constellation-node--central .constellation-node__sphere {
  border-color: oklch(1 0 0 / 0.16);
  background: radial-gradient(circle at 35% 25%, var(--color-brand-400), var(--color-accent-500) 56%, var(--color-brand-700));
}

.constellation-node--central .constellation-node__label {
  max-width: none;
  font-size: 28px;
  letter-spacing: 0;
}

.constellation-node__ring {
  position: absolute;
  inset: -7px;
  border-radius: inherit;
  background: conic-gradient(from 90deg, var(--color-brand-500), var(--color-accent-500), var(--color-brand-500));
  animation: constellation-ring 20s linear infinite;
}

.constellation-node__ring::after {
  content: '';
  position: absolute;
  inset: 2px;
  border-radius: inherit;
  background: var(--color-surface-900);
}

.constellation-node--person {
  --node-color: var(--color-brand-500);
}

.constellation-node--backend {
  --node-color: var(--color-brand-500);
}

.constellation-node--ai-ml {
  --node-color: var(--color-accent-500);
}

.constellation-node--infra {
  --node-color: var(--color-infra-500, oklch(0.70 0.15 200));
}

.constellation-node--frontend {
  --node-color: var(--color-frontend-500, oklch(0.70 0.18 50));
}

@keyframes constellation-ring {
  to { transform: rotate(360deg); }
}

@keyframes constellation-vibration {
  0%, 100% { transform: translate(-50%, -50%) scale(var(--node-scale)) rotate(0deg); }
  25% { transform: translate(calc(-50% + 1px), calc(-50% - 1px)) scale(var(--node-scale)) rotate(-0.5deg); }
  50% { transform: translate(calc(-50% - 1px), calc(-50% + 1px)) scale(var(--node-scale)) rotate(0.45deg); }
  75% { transform: translate(calc(-50% + 0.5px), calc(-50% + 1px)) scale(var(--node-scale)) rotate(-0.25deg); }
}

@keyframes constellation-top-pulse {
  0% {
    opacity: 0.48;
    transform: scale(0.88);
  }
  68%, 100% {
    opacity: 0;
    transform: scale(1.35);
  }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-node,
  .constellation-node__ring,
  .constellation-node::after {
    animation: none !important;
    transition: none !important;
  }
}
</style>
