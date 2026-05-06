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
      class="constellation-hero__search"
      @submit="search"
      @clear="clearSearch"
    />

    <p v-if="errorMessage" class="constellation-hero__error" role="alert">
      {{ errorMessage }}
    </p>

    <div class="constellation-hero__stage" role="group" aria-label="Constelación semántica del portfolio">
      <svg class="constellation-hero__edges" aria-hidden="true">
        <line
          v-for="node in nonCentralNodes"
          :key="`edge-${node.id}`"
          :x1="`${positionMap[node.id]?.x || 50}%`"
          :y1="`${positionMap[node.id]?.y || 50}%`"
          :x2="`${centralPosition.x}%`"
          :y2="`${centralPosition.y}%`"
        />
      </svg>

      <ConstellationNode
        v-for="(node, index) in tabOrderedNodes"
        :key="node.id"
        :node="node"
        :position="positionMap[node.id] || centralPosition"
        :visual="visualMap[node.id]"
        :reduced-motion="reducedMotion"
        :tabindex="index + 1"
        @select="handleExpandNode"
      />
    </div>

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
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useConstellation } from '../composables/useConstellation'
import ConstellationDetail from './ConstellationDetail.vue'
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

const reducedMotion = ref(false)
const activeNodeId = ref('')
const heroRef = ref(null)
const centralPosition = { x: 50, y: 48 }

const colorByCategory = {
  person: 'var(--color-brand-500)',
  backend: 'var(--color-brand-500)',
  'ai-ml': 'var(--color-accent-500)',
  infra: 'var(--color-infra-500, oklch(0.70 0.15 200))',
  frontend: 'var(--color-frontend-500, oklch(0.70 0.18 50))',
}

const nonCentralNodes = computed(() => nodes.value.filter((node) => !node.is_central))

const tabOrderedNodes = computed(() => {
  if (status.value === 'results' || status.value === 'expanded') return rankedNodes.value
  return nodes.value
})

const positionMap = computed(() => {
  const map = {}
  const orbitNodes = [...nonCentralNodes.value].sort((a, b) => {
    if (typeof a.score === 'number' || typeof b.score === 'number') return (b.score ?? -1) - (a.score ?? -1)
    return a.name.localeCompare(b.name)
  })

  nodes.value.forEach((node) => {
    if (node.is_central) map[node.id] = centralPosition
  })

  const idlePositions = [
    { x: 26, y: 38 },
    { x: 74, y: 38 },
    { x: 50, y: 76 },
    { x: 20, y: 68 },
    { x: 80, y: 68 },
  ]

  orbitNodes.forEach((node, index) => {
    if (typeof node.score !== 'number') {
      map[node.id] = idlePositions[index % idlePositions.length]
      return
    }

    const angle = (-90 + index * (360 / Math.max(orbitNodes.length, 1))) * (Math.PI / 180)
    const radius = node.score > 0.7 ? 17 : node.score >= 0.4 ? 25 : 34
    map[node.id] = {
      x: 50 + Math.cos(angle) * radius,
      y: 50 + Math.sin(angle) * radius * 0.72,
    }
  })

  return map
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

const closeConstellation = () => {
  emit('close')
}

const getFocusableElements = () => {
  if (!heroRef.value) return []
  return [...heroRef.value.querySelectorAll('button, input, a[href], [tabindex]:not([tabindex="-1"])')]
    .filter((element) => element !== heroRef.value && !element.disabled && element.offsetParent !== null)
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    if (selectedNode.value) {
      closeDetail()
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

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
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
let introContext = null
let previousActiveElement = null

const handleMotionChange = (event) => {
  reducedMotion.value = event.matches
}

onMounted(() => {
  previousActiveElement = document.activeElement
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = mediaQuery.matches
  mediaQuery.addEventListener?.('change', handleMotionChange)

  if (!reducedMotion.value) {
    introContext = gsap.context(() => {
      gsap.fromTo('.constellation-hero__intro > *, .constellation-hero__search', { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.08, ease: 'power3.out' })
    })
  }

  nextTick(() => {
    heroRef.value?.querySelector('#constellation-query')?.focus()
  })
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener?.('change', handleMotionChange)
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
  grid-template-rows: auto auto auto 1fr;
  align-items: start;
  min-height: 100vh;
  overflow: hidden;
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

.constellation-hero__stage {
  position: relative;
  z-index: 1;
  width: min(1120px, 100%);
  min-height: 430px;
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

.constellation-hero__edges line {
  stroke: var(--color-edge-faint, oklch(1 0 0 / 0.08));
  stroke-width: 1;
}

@media (max-width: 760px) {
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

  .constellation-hero__stage {
    min-height: 520px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-hero * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
