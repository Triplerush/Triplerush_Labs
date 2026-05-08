<template>
  <section
    v-if="open"
    ref="heroRef"
    class="constellation-hero"
    role="dialog"
    aria-modal="true"
    aria-labelledby="constellation-title"
    tabindex="-1"
    @keydown="handleKeydown"
  >
    <div class="constellation-hero__background" aria-hidden="true">
      <div class="constellation-hero__grid"></div>
      <div class="constellation-hero__glow constellation-hero__glow--brand"></div>
      <div class="constellation-hero__glow constellation-hero__glow--accent"></div>
    </div>

    <button type="button" class="constellation-hero__classic" @click="closeConstellation">
      Ver portfolio clásico
    </button>

    <div class="constellation-hero__intro">
      <p class="constellation-hero__eyebrow">Portfolio interactivo con RAG</p>
      <h1 id="constellation-title">Fernando Canal</h1>
      <p>Busca una capacidad y la constelación ordena proyectos, experiencia y formación por relevancia semántica.</p>
    </div>

    <ConstellationSearch
      v-model="query"
      :is-searching="status === 'searching'"
      :contextual-suggestions="contextualSuggestions"
      class="constellation-hero__search"
      @submit="search"
      @clear="clearSearch"
    />

    <p v-if="errorMessage" class="constellation-hero__error" role="alert">
      {{ errorMessage }}
    </p>

    <div v-if="isMobileFallback && status === 'searching'" class="constellation-hero__mobile-loading" role="status" aria-live="polite">
      <span class="constellation-hero__searching-orbit" aria-hidden="true"></span>
      Reordenando resultados
    </div>

    <div
      v-if="!isMobileFallback"
      ref="stageRef"
      class="constellation-hero__stage"
      role="group"
      aria-label="Constelación semántica del portfolio"
    >
      <svg class="constellation-hero__edges" aria-hidden="true">
        <circle
          v-for="point in trailPoints"
          :key="point.id"
          class="constellation-hero__trail"
          r="2"
          :cx="`${point.x}%`"
          :cy="`${point.y}%`"
          :style="{ '--trail-color': point.color, '--trail-opacity-factor': point.opacity }"
        />
        <line
          v-for="node in nonCentralNodes"
          :key="`edge-${node.id}`"
          class="constellation-hero__edge"
          :class="{ 'constellation-hero__edge--active': hoveredNodeId === node.id || activeNodeId === node.id }"
          :x1="`${positionMap[node.id]?.x || 50}%`"
          :y1="`${positionMap[node.id]?.y || 50}%`"
          :x2="`${centralPosition.x}%`"
          :y2="`${centralPosition.y}%`"
          :style="{ '--edge-strength': edgeStrength(node) }"
        />
      </svg>

      <div v-if="status === 'searching'" class="constellation-hero__searching" role="status" aria-live="polite">
        <span class="constellation-hero__searching-orbit" aria-hidden="true"></span>
        <span>Reordenando constelación</span>
      </div>

      <ConstellationNode
        v-for="(node, index) in tabOrderedNodes"
        :key="node.id"
        :node="node"
        :position="positionMap[node.id] || centralPosition"
        :visual="visualMap[node.id]"
        :reduced-motion="reducedMotion"
        :agitated="node.is_central && isCentralAgitated"
        :pulse-rank="pulseRankMap[node.id] || 0"
        :tabindex="0"
        @select="handleExpandNode"
        @node-hover="hoveredNodeId = node.id"
        @node-leave="hoveredNodeId = ''"
        @node-drag-start="startDrag"
        @node-drag="drag"
        @node-drag-end="endDrag"
      />
    </div>

    <ConstellationFallback
      v-else
      :nodes="tabOrderedNodes"
      :reduced-motion="reducedMotion"
      @select="handleExpandNode"
    />

    <div role="status" aria-live="polite" class="sr-only">
      {{ lastAnnouncement }}
    </div>

    <ConstellationDetail
      v-if="selectedNode"
      :node="selectedNode"
      :reduced-motion="reducedMotion"
      @close="handleCloseDetail"
    />
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { useConstellation } from '../composables/useConstellation'
import { useConstellationPhysics } from '../composables/useConstellationPhysics'
import ConstellationDetail from './ConstellationDetail.vue'
import ConstellationFallback from './ConstellationFallback.vue'
import ConstellationNode from './ConstellationNode.vue'
import ConstellationSearch from './ConstellationSearch.vue'

defineProps({
  open: { type: Boolean, default: true },
})

const emit = defineEmits(['close'])

const {
  status,
  query,
  nodes,
  rankedNodes,
  selectedNode,
  errorMessage,
  lastAnnouncement,
  search,
  expandNode,
  closeDetail,
  clearSearch,
} = useConstellation()

const reducedMotion = ref(typeof window !== 'undefined' ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false)
const isMobileFallback = ref(typeof window !== 'undefined' ? window.matchMedia('(max-width: 767px)').matches : false)
const activeNodeId = ref('')
const hoveredNodeId = ref('')
const heroRef = ref(null)
const stageRef = ref(null)
const stageSize = ref({ width: 1120, height: 430 })
const physicsReducedMotion = computed(() => reducedMotion.value || isMobileFallback.value)

const {
  centralPosition,
  positionMap,
  trailPoints,
  isCentralAgitated,
  startDrag,
  drag,
  endDrag,
} = useConstellationPhysics({ nodes, stageSize, reducedMotion: physicsReducedMotion })

const colorByCategory = {
  person: 'var(--color-brand-500)',
  backend: 'var(--color-brand-500)',
  'ai-ml': 'var(--color-accent-500)',
  infra: 'var(--color-infra-500, oklch(0.70 0.15 200))',
  frontend: 'var(--color-frontend-500, oklch(0.70 0.18 50))',
}

const nonCentralNodes = computed(() => nodes.value.filter((node) => !node.is_central))

const topScoredNodes = computed(() => rankedNodes.value
  .filter((node) => !node.is_central && typeof node.score === 'number')
  .slice(0, 3))

const pulseRankMap = computed(() => {
  if (status.value !== 'results' && status.value !== 'expanded') return {}
  return topScoredNodes.value.reduce((map, node, index) => {
    map[node.id] = index + 1
    return map
  }, {})
})

const normalizeChip = (value) => String(value || '').trim().replace(/\s+/g, ' ')

const contextualSuggestions = computed(() => {
  if (status.value !== 'results' && status.value !== 'expanded') return []

  const seen = new Set()
  const chips = []
  const addChip = (value) => {
    const chip = normalizeChip(value)
    const key = chip.toLocaleLowerCase()
    if (!chip || chip.length < 3 || seen.has(key)) return
    seen.add(key)
    chips.push(chip)
  }

  topScoredNodes.value.forEach((node) => {
    addChip(node.name)
    addChip(node.category)
    ;(node.data?.demonstrates || []).forEach(addChip)
    ;(node.data?.stack || []).forEach(addChip)
  })

  return chips.slice(0, 8)
})

const tabOrderedNodes = computed(() => {
  if (status.value === 'results' || status.value === 'expanded') return rankedNodes.value
  return nodes.value
})

const visualMap = computed(() => {
  const map = {}

  nodes.value.forEach((node) => {
    if (node.is_central) {
      map[node.id] = {
        scale: 1,
        opacity: 1,
        glow: '0 0 30px oklch(0.55 0.20 250 / 0.5)',
        color: colorByCategory.person,
      }
      return
    }

    if (typeof node.score !== 'number') {
      map[node.id] = {
        scale: 1,
        opacity: 0.82,
        glow: '0 0 0 oklch(0 0 0 / 0)',
        color: colorByCategory[node.category] || colorByCategory.backend,
      }
      return
    }

    const visual = node.score > 0.7
      ? { scale: 1.5, opacity: 1, glow: '0 0 40px var(--color-glow-active, oklch(0.65 0.20 250 / 0.6))' }
      : node.score >= 0.4
        ? { scale: 1, opacity: 0.62, glow: '0 0 10px oklch(0.55 0.20 250 / 0.3)' }
        : { scale: 0.55, opacity: 0.28, glow: '0 0 0 oklch(0 0 0 / 0)' }

    map[node.id] = {
      ...visual,
      color: colorByCategory[node.category] || colorByCategory.backend,
    }
  })

  return map
})

const edgeStrength = (node) => {
  if (hoveredNodeId.value === node.id || activeNodeId.value === node.id) return 1
  if (typeof node.score !== 'number') return 0.36
  return Math.max(0.18, Math.min(0.9, node.score))
}

const closeConstellation = () => {
  emit('close')
}

const getFocusableElements = () => {
  if (!heroRef.value) return []
  const focusScope = selectedNode.value
    ? heroRef.value.querySelector('.constellation-detail')
    : heroRef.value
  if (!focusScope) return []

  return [...focusScope.querySelectorAll('button, input, textarea, a[href], [tabindex]:not([tabindex="-1"])')]
    .filter((element) => element !== heroRef.value && !element.disabled && element.offsetParent !== null)
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    if (selectedNode.value) {
      handleCloseDetail()
    } else {
      closeConstellation()
    }
    return
  }

  if (event.key !== 'Tab') return

  const focusableElements = getFocusableElements()
  if (!focusableElements.length) return

  const first = focusableElements[0]
  const last = focusableElements[focusableElements.length - 1]
  const activeElement = document.activeElement

  if (selectedNode.value && !focusableElements.includes(activeElement)) {
    event.preventDefault()
    if (event.shiftKey) {
      last.focus()
    } else {
      first.focus()
    }
    return
  }

  if (event.shiftKey && activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

const handleExpandNode = (node) => {
  activeNodeId.value = node.id
  expandNode(node)
}

const handleCloseDetail = () => {
  closeDetail()
  requestAnimationFrame(() => {
    document.querySelector(`[data-node-id="${activeNodeId.value}"]`)?.focus()
  })
}

let mediaQuery = null
let mobileQuery = null
let introContext = null
let previousActiveElement = null
let resizeObserver = null

const handleMotionChange = (event) => {
  reducedMotion.value = event.matches
}

const handleMobileChange = (event) => {
  isMobileFallback.value = event.matches
}

const updateStageSize = () => {
  if (!stageRef.value) return
  const rect = stageRef.value.getBoundingClientRect()
  stageSize.value = {
    width: Math.max(320, rect.width),
    height: Math.max(360, rect.height),
  }
}

const observeStage = () => {
  resizeObserver?.disconnect()
  if (stageRef.value) {
    resizeObserver?.observe(stageRef.value)
    updateStageSize()
  }
}

onMounted(() => {
  previousActiveElement = document.activeElement
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = mediaQuery.matches
  mediaQuery.addEventListener?.('change', handleMotionChange)
  mobileQuery = window.matchMedia('(max-width: 767px)')
  isMobileFallback.value = mobileQuery.matches
  mobileQuery.addEventListener?.('change', handleMobileChange)
  updateStageSize()

  resizeObserver = new ResizeObserver(updateStageSize)
  observeStage()

  if (!reducedMotion.value && !isMobileFallback.value) {
    introContext = gsap.context(() => {
      gsap.fromTo('.constellation-hero__intro > *, .constellation-hero__search', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.08, ease: 'power3.out' })
    })
  }

  nextTick(() => {
    heroRef.value?.querySelector('#constellation-query')?.focus()
  })
})

watch(isMobileFallback, async () => {
  await nextTick()
  observeStage()
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener?.('change', handleMotionChange)
  mobileQuery?.removeEventListener?.('change', handleMobileChange)
  resizeObserver?.disconnect()
  introContext?.revert()
  previousActiveElement?.focus?.()
})
</script>

<style scoped>
.constellation-hero {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: grid;
  grid-template-rows: auto auto auto minmax(420px, 1fr);
  align-items: start;
  min-height: 100dvh;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  background: var(--color-surface-900);
  color: oklch(0.94 0.01 250);
}

.constellation-hero__background,
.constellation-hero__grid,
.constellation-hero__glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.constellation-hero__grid {
  opacity: 0.08;
  background-image:
    linear-gradient(oklch(1 0 0 / 0.14) 1px, transparent 1px),
    linear-gradient(90deg, oklch(1 0 0 / 0.14) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(circle at center, black, transparent 78%);
}

.constellation-hero__glow {
  filter: blur(90px);
  opacity: 0.22;
}

.constellation-hero__glow--brand {
  inset: 12% auto auto 8%;
  width: 360px;
  height: 360px;
  border-radius: 999px;
  background: var(--color-brand-500);
}

.constellation-hero__glow--accent {
  inset: auto 10% 6% auto;
  width: 320px;
  height: 320px;
  border-radius: 999px;
  background: var(--color-accent-500);
}

.constellation-hero__classic {
  position: relative;
  z-index: 6;
  justify-self: end;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid oklch(1 0 0 / 0.14);
  border-radius: 12px;
  background: oklch(1 0 0 / 0.06);
  color: oklch(0.94 0.01 250);
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  backdrop-filter: blur(12px);
}

.constellation-hero__classic:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 2px;
}

.constellation-hero__intro {
  position: relative;
  z-index: 2;
  justify-self: center;
  width: min(760px, calc(100vw - 32px));
  margin-top: 12px;
  text-align: center;
}

.constellation-hero__eyebrow {
  margin: 0 0 8px;
  color: var(--color-brand-300);
  font-family: var(--font-mono);
  font-size: 12px;
  text-transform: uppercase;
}

.constellation-hero__intro h1 {
  margin: 0;
  font-size: clamp(44px, 8vw, 92px);
  line-height: 0.94;
  font-weight: 950;
  background: linear-gradient(135deg, var(--color-brand-400), var(--color-accent-400));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.constellation-hero__intro p:last-child {
  max-width: 650px;
  margin: 14px auto 0;
  color: oklch(0.90 0.01 250 / 0.66);
  font-size: 15px;
  line-height: 1.55;
}

.constellation-hero__search {
  position: relative;
  z-index: 5;
  justify-self: center;
  margin-top: 22px;
}

.constellation-hero__error {
  position: relative;
  z-index: 5;
  justify-self: center;
  width: min(760px, calc(100vw - 32px));
  margin: 12px 0 0;
  padding: 10px 14px;
  border: 1px solid oklch(0.65 0.20 25 / 0.26);
  border-radius: 14px;
  background: oklch(0.30 0.12 25 / 0.22);
  color: oklch(0.88 0.08 35);
  font-size: 13px;
  text-align: center;
}

.constellation-hero__mobile-loading {
  position: relative;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  justify-self: center;
  gap: 10px;
  margin-top: 12px;
  padding: 10px 13px;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 999px;
  background: oklch(0.10 0.02 250 / 0.72);
  color: oklch(0.94 0.01 250);
  font-size: 13px;
  font-weight: 800;
}

.constellation-hero__stage {
  position: relative;
  z-index: 1;
  width: min(1120px, 100%);
  min-height: min(520px, max(420px, calc(100dvh - 310px)));
  justify-self: center;
  align-self: stretch;
}

.constellation-hero__edges {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.constellation-hero__edge {
  stroke: var(--color-edge-faint, oklch(1 0 0 / 0.08));
  stroke-width: var(--constellation-edge-width-rest, 1px);
  stroke-linecap: round;
  opacity: max(var(--constellation-edge-opacity-rest, 0.10), var(--edge-strength, 0.35));
  transition:
    stroke var(--constellation-motion-fast, 160ms) var(--constellation-ease-out, ease),
    opacity var(--constellation-motion-fast, 160ms) var(--constellation-ease-out, ease),
    stroke-width var(--constellation-motion-fast, 160ms) var(--constellation-ease-out, ease),
    filter var(--constellation-motion-fast, 160ms) var(--constellation-ease-out, ease);
}

.constellation-hero__edge--active {
  stroke: var(--color-glow-active, oklch(0.65 0.20 250 / 0.72));
  stroke-width: var(--constellation-edge-width-active, 2.2px);
  opacity: var(--constellation-edge-opacity-active, 0.62);
  filter: drop-shadow(0 0 10px var(--color-glow-active, oklch(0.65 0.20 250 / 0.72)));
}

.constellation-hero__trail {
  fill: var(--trail-color, var(--color-brand-500));
  opacity: calc(var(--constellation-trail-opacity, 0.18) * var(--trail-opacity-factor, 1));
  filter: blur(var(--constellation-trail-blur, 2px));
  pointer-events: none;
}

.constellation-hero__searching {
  position: absolute;
  left: 50%;
  top: 52%;
  z-index: 8;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid oklch(1 0 0 / 0.12);
  border-radius: 999px;
  background: oklch(0.10 0.02 250 / 0.78);
  box-shadow: 0 18px 70px oklch(0 0 0 / 0.32);
  color: oklch(0.94 0.01 250);
  font-size: 13px;
  font-weight: 800;
  transform: translate(-50%, -50%);
  backdrop-filter: blur(16px);
}

.constellation-hero__searching-orbit {
  width: 18px;
  height: 18px;
  border: 2px solid oklch(1 0 0 / 0.22);
  border-top-color: var(--color-brand-300);
  border-right-color: var(--color-accent-400);
  border-radius: 999px;
  animation: constellation-hero-orbit 850ms linear infinite;
}

@keyframes constellation-hero-orbit {
  to { transform: rotate(360deg); }
}

@media (max-width: 767px) {
  .constellation-hero {
    grid-template-rows: auto auto auto auto 1fr;
    padding: 14px;
    overflow-y: auto;
  }

  .constellation-hero__classic {
    justify-self: stretch;
  }

  .constellation-hero__intro {
    margin-top: 18px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-hero * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
