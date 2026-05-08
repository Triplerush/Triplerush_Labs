<template>
  <section
    ref="heroRef"
    class="hero"
    :class="[`hero--${phase}`]"
    role="region"
    aria-labelledby="constellation-title"
  >
    <vue-particles
      id="hero-particles"
      class="hero__particles"
      :options="particlesOptions"
    />

    <div class="hero__bg" aria-hidden="true">
      <div class="hero__glow hero__glow--cyan"></div>
      <div class="hero__glow hero__glow--violet"></div>
    </div>

    <header class="hero__topbar">
      <div class="hero__brand">
        <span class="hero__brand-name">Fernando Canal</span>
        <span class="hero__brand-divider" aria-hidden="true">·</span>
        <span class="hero__brand-tagline">AI Software Engineer</span>
      </div>
      <a
        class="hero__github"
        href="https://github.com/triplerush"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="GitHub"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      </a>
    </header>

    <div class="hero__intro" :aria-hidden="phase !== 'intro'">
      <p class="hero__eyebrow">Portfolio interactivo · Búsqueda semántica</p>
      <h1 id="constellation-title" class="hero__name">Fernando Canal</h1>
      <p class="hero__lead">AI Software Engineer · Building AI that ships to production</p>
      <p class="hero__hint">{{ introHint }}</p>
    </div>

    <div class="hero__layout">
      <!-- Left explorer panel -->
      <aside v-if="!isMobileFallback" class="hero__sidebar" aria-label="Explorar nodos">
        <div class="hero__sidebar-header">
          <span class="hero__sidebar-title">Explorar</span>
          <span class="hero__sidebar-count">{{ nodes.length }}</span>
        </div>

        <div v-for="group in nodeGroups" :key="group.type" class="hero__sidebar-group">
          <p class="hero__sidebar-group-title">{{ group.label }}</p>
          <ul class="hero__sidebar-list">
            <li v-for="node in group.items" :key="node.id">
              <button
                type="button"
                class="hero__sidebar-item"
                :class="{
                  'hero__sidebar-item--top': topRankMap[node.id] === 1,
                  'hero__sidebar-item--hovered': hoveredNodeId === node.id,
                }"
                @mouseenter="hoveredNodeId = node.id"
                @mouseleave="hoveredNodeId = ''"
                @focus="hoveredNodeId = node.id"
                @blur="hoveredNodeId = ''"
                @click="handleExpandNode(node)"
              >
                <span class="hero__sidebar-dot" :class="`hero__sidebar-dot--${node.type}`" aria-hidden="true"></span>
                <span class="hero__sidebar-name">{{ sidebarLabel(node) }}</span>
                <span v-if="typeof node.score === 'number'" class="hero__sidebar-score">{{ node.score.toFixed(2) }}</span>
              </button>
            </li>
          </ul>
        </div>

        <div class="hero__sidebar-stats">
          <div class="hero__sidebar-stat">
            <span class="hero__sidebar-stat-key">Nodos</span>
            <span class="hero__sidebar-stat-value">{{ nodes.length }}</span>
          </div>
          <div class="hero__sidebar-stat">
            <span class="hero__sidebar-stat-key">Conexiones</span>
            <span class="hero__sidebar-stat-value">{{ edges.length }}</span>
          </div>
          <div v-if="searchActive" class="hero__sidebar-stat">
            <span class="hero__sidebar-stat-key">Mejor coincidencia</span>
            <span class="hero__sidebar-stat-value hero__sidebar-stat-value--accent">
              {{ topScore !== null ? topScore.toFixed(2) : '—' }}
            </span>
          </div>
        </div>
      </aside>

      <div class="hero__canvas">
        <div class="hero__search-block">
          <ConstellationSearch
            v-model="query"
            :is-searching="status === 'searching'"
            @submit="search"
            @clear="clearSearch"
          />
          <p v-if="errorMessage" class="hero__error" role="alert">{{ errorMessage }}</p>
        </div>

        <div
          v-if="isMobileFallback && status === 'searching'"
          class="hero__mobile-loading"
          role="status"
          aria-live="polite"
        >
          <span class="hero__searching-orbit" aria-hidden="true"></span>
          Reordenando resultados
        </div>

        <div
          v-if="!isMobileFallback"
          ref="stageRef"
          class="hero__stage"
          role="group"
          aria-label="Constelación semántica del portfolio"
          @keydown="handleStageKeydown"
        >
          <svg class="hero__edges" aria-hidden="true">
            <line
              v-for="edge in renderableEdges"
              :key="edge.id"
              class="hero__edge"
              :class="{
                'hero__edge--active': edge.active,
                'hero__edge--top': edge.top,
                'hero__edge--dim': edge.dim,
              }"
              :x1="`${edge.x1}%`"
              :y1="`${edge.y1}%`"
              :x2="`${edge.x2}%`"
              :y2="`${edge.y2}%`"
            />
          </svg>

          <div v-if="status === 'searching'" class="hero__searching" role="status" aria-live="polite">
            <span class="hero__searching-orbit" aria-hidden="true"></span>
            <span>Reordenando</span>
          </div>

          <ConstellationNode
            v-for="node in tabOrderedNodes"
            :key="node.id"
            :node="node"
            :position="positionMap[node.id] || { x: 50, y: 50 }"
            :visual="visualMap[node.id]"
            :top-rank="topRankMap[node.id] || 0"
            :reduced-motion="reducedMotion"
            :related="hoveredNodeId ? hoveredRelatedIds.has(node.id) || node.id === hoveredNodeId : false"
            :muted="hoveredNodeId ? !hoveredRelatedIds.has(node.id) && node.id !== hoveredNodeId : false"
            :tabindex="0"
            @select="handleExpandNode"
            @node-hover="hoveredNodeId = node.id"
            @node-leave="hoveredNodeId = ''"
            @node-drag-start="startDrag"
            @node-drag="drag"
            @node-drag-end="endDrag"
          />

          <div
            v-if="hoverCard.node"
            class="hero__hover-card"
            :style="hoverCard.style"
            aria-hidden="true"
          >
            <span class="hero__hover-card-type">{{ hoverCard.typeLabel }}</span>
            <span class="hero__hover-card-name">{{ hoverCard.node.name }}</span>
            <span v-if="hoverCard.summary" class="hero__hover-card-summary">{{ hoverCard.summary }}</span>
            <span v-if="hoverCard.scoreLabel" class="hero__hover-card-score">{{ hoverCard.scoreLabel }}</span>
          </div>
        </div>

        <ConstellationFallback
          v-else
          :nodes="tabOrderedNodes"
          :reduced-motion="reducedMotion"
          @select="handleExpandNode"
        />
      </div>
    </div>

    <div role="status" aria-live="polite" class="sr-only">{{ lastAnnouncement }}</div>

    <ConstellationDetail
      v-if="selectedNode"
      :node="selectedNode"
      :related-nodes="selectedRelatedNodes"
      :reduced-motion="reducedMotion"
      @close="handleCloseDetail"
      @navigate="handleNavigate"
    />
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useConstellation } from '../composables/useConstellation'
import { useConstellationPhysics } from '../composables/useConstellationPhysics'
import ConstellationDetail from './ConstellationDetail.vue'
import ConstellationFallback from './ConstellationFallback.vue'
import ConstellationNode from './ConstellationNode.vue'
import ConstellationSearch from './ConstellationSearch.vue'

const {
  status,
  query,
  nodes,
  rankedNodes,
  selectedNode,
  errorMessage,
  lastAnnouncement,
  searchActive,
  search,
  expandNode,
  focusNodeById,
  closeDetail,
  clearSearch,
} = useConstellation()

const reducedMotion = ref(typeof window !== 'undefined' ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false)
const isMobileFallback = ref(typeof window !== 'undefined' ? window.matchMedia('(max-width: 767px)').matches : false)
const hoveredNodeId = ref('')
const heroRef = ref(null)
const stageRef = ref(null)
const stageSize = ref({ width: 1180, height: 600 })
const physicsReducedMotion = computed(() => reducedMotion.value || isMobileFallback.value)

const phase = ref('intro')
const introHint = ref('Cargando constelación…')
let introTimer = null
let skipHandler = null

const particlesOptions = {
  fullScreen: { enable: false },
  background: { color: 'transparent' },
  fpsLimit: 60,
  particles: {
    number: { value: 56, density: { enable: true, area: 1100 } },
    color: { value: ['#00E5FF', '#E8EAED'] },
    shape: { type: 'circle' },
    opacity: { value: { min: 0.08, max: 0.30 } },
    size: { value: { min: 1, max: 2 } },
    move: { enable: true, speed: 0.35, direction: 'none', outModes: 'bounce' },
    links: { enable: true, distance: 130, color: '#00E5FF', opacity: 0.08, width: 1 },
  },
  interactivity: {
    detectsOn: 'window',
    events: { onHover: { enable: true, mode: 'grab' } },
    modes: { grab: { distance: 180, links: { opacity: 0.32 } } },
  },
  detectRetina: true,
}

const {
  positionMap,
  edges,
  connectedIds,
  nodeRadii,
  startDrag,
  drag,
  endDrag,
} = useConstellationPhysics({
  nodes,
  stageSize,
  reducedMotion: physicsReducedMotion,
  searchActive,
})

const hoveredRelatedIds = computed(() => {
  if (!hoveredNodeId.value) return new Set()
  return connectedIds(hoveredNodeId.value)
})

const tabOrderedNodes = computed(() => searchActive.value ? rankedNodes.value : nodes.value)

const topRankMap = computed(() => {
  if (!searchActive.value) return {}
  const scored = nodes.value
    .filter((n) => !n.is_central && typeof n.score === 'number')
    .sort((a, b) => b.score - a.score)
  const map = {}
  scored.forEach((node, idx) => {
    map[node.id] = idx + 1
  })
  return map
})

const topScore = computed(() => {
  if (!searchActive.value) return null
  const scored = nodes.value
    .filter((n) => !n.is_central && typeof n.score === 'number')
    .sort((a, b) => b.score - a.score)
  return scored[0]?.score ?? null
})

const visualMap = computed(() => {
  const map = {}
  const ranks = topRankMap.value

  nodes.value.forEach((node) => {
    if (node.is_central) {
      map[node.id] = {
        scale: searchActive.value ? 0.92 : 1,
        opacity: searchActive.value ? 0.7 : 1,
      }
      return
    }

    if (!searchActive.value) {
      map[node.id] = { scale: 1, opacity: 0.94 }
      return
    }

    const rank = ranks[node.id] || 99
    if (rank === 1) {
      map[node.id] = { scale: 1.18, opacity: 1 }
    } else if (rank === 2) {
      map[node.id] = { scale: 1.08, opacity: 0.92 }
    } else if (rank === 3) {
      map[node.id] = { scale: 1.02, opacity: 0.82 }
    } else {
      map[node.id] = { scale: 0.78, opacity: 0.34 }
    }
  })

  return map
})

// Trim edges so they stop at each node's outer radius instead of running through
// the node fill. Skip very-short edges (where source and target circles overlap).
const renderableEdges = computed(() => {
  const list = []
  const hovered = hoveredNodeId.value
  const ranks = topRankMap.value
  const topIds = new Set(
    Object.entries(ranks)
      .filter(([, rank]) => rank <= 3)
      .map(([id]) => id),
  )
  const stageW = stageSize.value.width
  const stageH = stageSize.value.height
  if (!stageW || !stageH) return list

  const radii = nodeRadii.value

  edges.value.forEach((edge) => {
    const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id
    const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id
    const source = positionMap.value[sourceId]
    const target = positionMap.value[targetId]
    if (!source || !target) return

    const sx = (source.x / 100) * stageW
    const sy = (source.y / 100) * stageH
    const tx = (target.x / 100) * stageW
    const ty = (target.y / 100) * stageH
    const dx = tx - sx
    const dy = ty - sy
    const dist = Math.hypot(dx, dy)

    const sourceR = (radii[sourceId] ?? 50) + 4
    const targetR = (radii[targetId] ?? 50) + 4
    if (dist < sourceR + targetR + 8) return // would render entirely inside the nodes

    const ux = dx / dist
    const uy = dy / dist
    const x1px = sx + ux * sourceR
    const y1px = sy + uy * sourceR
    const x2px = tx - ux * targetR
    const y2px = ty - uy * targetR

    const active = hovered && (sourceId === hovered || targetId === hovered)
    const top = !hovered && searchActive.value && (topIds.has(sourceId) || topIds.has(targetId))
    const dim = Boolean(hovered) && !active

    list.push({
      id: `${sourceId}-${targetId}`,
      x1: (x1px / stageW) * 100,
      y1: (y1px / stageH) * 100,
      x2: (x2px / stageW) * 100,
      y2: (y2px / stageH) * 100,
      active,
      top,
      dim,
    })
  })

  return list
})

const selectedRelatedNodes = computed(() => {
  if (!selectedNode.value) return []
  const ids = connectedIds(selectedNode.value.id)
  return nodes.value.filter((node) => ids.has(node.id))
})

const sidebarTypeLabels = {
  person: 'Persona',
  experience: 'Experiencia',
  education: 'Formación',
  skill: 'Skills',
  project: 'Proyecto',
}

const sidebarLabel = (node) => {
  const data = node.data || {}
  if (node.is_central) return 'Fernando Canal'
  if (node.type === 'experience') return data.company || node.name
  return node.name
}

const nodeGroups = computed(() => {
  const order = ['person', 'experience', 'education', 'skill', 'project']
  const groups = {}
  order.forEach((t) => { groups[t] = [] })

  const list = searchActive.value ? rankedNodes.value : nodes.value
  list.forEach((node) => {
    if (groups[node.type]) groups[node.type].push(node)
  })

  return order
    .filter((t) => groups[t].length > 0)
    .map((t) => ({
      type: t,
      label: sidebarTypeLabels[t] || t,
      items: groups[t],
    }))
})

const hoverCard = computed(() => {
  const id = hoveredNodeId.value
  if (!id) return { node: null }
  const node = nodes.value.find((n) => n.id === id)
  if (!node) return { node: null }

  const pos = positionMap.value[id]
  if (!pos) return { node: null }

  const data = node.data || {}
  const summary = data.summary || data.description || ''
  const scoreLabel = typeof node.score === 'number' ? `Coincidencia ${node.score.toFixed(2)}` : ''

  return {
    node,
    typeLabel: sidebarTypeLabels[node.type] || 'Nodo',
    summary: summary.length > 140 ? `${summary.slice(0, 137)}…` : summary,
    scoreLabel,
    style: {
      left: `${pos.x}%`,
      top: `${pos.y}%`,
    },
  }
})

const enterGraphPhase = () => {
  if (phase.value === 'graph') return
  phase.value = 'graph'
}

const handleStageKeydown = (event) => {
  if (event.key === 'Escape' && selectedNode.value) {
    handleCloseDetail()
  }
}

const lastFocusedNodeId = ref('')

const handleExpandNode = (node) => {
  lastFocusedNodeId.value = node.id
  expandNode(node)
}

const handleNavigate = (nodeId) => {
  lastFocusedNodeId.value = nodeId
  focusNodeById(nodeId)
}

const handleCloseDetail = () => {
  closeDetail()
  requestAnimationFrame(() => {
    document.querySelector(`[data-node-id="${lastFocusedNodeId.value}"]`)?.focus()
  })
}

let mediaQuery = null
let mobileQuery = null
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

watch(phase, async () => {
  await nextTick()
  updateStageSize()
})

watch(searchActive, (active) => {
  if (active && phase.value === 'intro') {
    enterGraphPhase()
  }
})

onMounted(() => {
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = mediaQuery.matches
  mediaQuery.addEventListener?.('change', handleMotionChange)
  mobileQuery = window.matchMedia('(max-width: 767px)')
  isMobileFallback.value = mobileQuery.matches
  mobileQuery.addEventListener?.('change', handleMobileChange)
  updateStageSize()

  resizeObserver = new ResizeObserver(updateStageSize)
  observeStage()

  if (reducedMotion.value) {
    phase.value = 'graph'
    return
  }

  setTimeout(() => {
    introHint.value = 'Pulsa o desliza para continuar'
  }, 1100)

  introTimer = setTimeout(enterGraphPhase, 2400)

  skipHandler = () => {
    if (phase.value === 'intro') enterGraphPhase()
  }
  document.addEventListener('pointerdown', skipHandler)
  document.addEventListener('wheel', skipHandler, { passive: true })
  document.addEventListener('keydown', skipHandler)
})

watch(isMobileFallback, async () => {
  await nextTick()
  observeStage()
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener?.('change', handleMotionChange)
  mobileQuery?.removeEventListener?.('change', handleMobileChange)
  resizeObserver?.disconnect()
  if (introTimer) clearTimeout(introTimer)
  if (skipHandler) {
    document.removeEventListener('pointerdown', skipHandler)
    document.removeEventListener('wheel', skipHandler)
    document.removeEventListener('keydown', skipHandler)
  }
})
</script>

<style scoped>
.hero {
  position: fixed;
  inset: 0;
  z-index: 10;
  display: grid;
  grid-template-rows: auto 1fr;
  align-items: stretch;
  justify-items: stretch;
  min-height: 100dvh;
  overflow: hidden;
  background: var(--color-bg);
  color: var(--color-text);
}

.hero__particles {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.hero__particles :deep(canvas) {
  pointer-events: none !important;
}

.hero__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.hero__glow {
  position: absolute;
  filter: blur(140px);
  border-radius: 999px;
  pointer-events: none;
  transition: opacity 600ms var(--constellation-ease-out);
}

.hero__glow--cyan {
  inset: -12% auto auto -10%;
  width: 480px;
  height: 480px;
  background: rgba(0, 229, 255, 0.10);
  opacity: 0.55;
}

.hero__glow--violet {
  inset: auto -10% -12% auto;
  width: 420px;
  height: 420px;
  background: rgba(139, 92, 246, 0.08);
  opacity: 0.55;
}

.hero--intro .hero__glow {
  opacity: 0.85;
}

/* Top bar */
.hero__topbar {
  position: relative;
  z-index: 6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 28px;
  border-bottom: 1px solid var(--color-border);
  background: rgba(8, 9, 11, 0.62);
  backdrop-filter: blur(14px);
  transition: opacity 480ms var(--constellation-ease-out),
              transform 480ms var(--constellation-ease-out);
}

.hero--intro .hero__topbar {
  opacity: 0;
  transform: translateY(-4px);
  pointer-events: none;
}

.hero__brand {
  display: inline-flex;
  align-items: baseline;
  gap: 10px;
  min-width: 0;
}

.hero__brand-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: -0.01em;
}

.hero__brand-divider {
  color: var(--color-muted-2);
  font-size: 12px;
}

.hero__brand-tagline {
  font-size: 12px;
  font-weight: 400;
  color: var(--color-muted);
  letter-spacing: 0.02em;
}

.hero__github {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: transparent;
  color: var(--color-muted);
  text-decoration: none;
  transition: border-color 200ms var(--constellation-ease-out),
              color 200ms var(--constellation-ease-out);
}

.hero__github:hover {
  border-color: var(--color-accent);
  color: var(--color-text);
}

.hero__github svg {
  width: 16px;
  height: 16px;
}

/* Intro overlay */
.hero__intro {
  position: absolute;
  inset: 0;
  z-index: 30;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 20px;
  padding: 24px;
  text-align: center;
  background: rgba(8, 9, 11, 0.55);
  backdrop-filter: blur(2px);
  transition: opacity 600ms var(--constellation-ease-out),
              transform 600ms var(--constellation-ease-out);
}

.hero--graph .hero__intro {
  opacity: 0;
  transform: scale(1.02);
  pointer-events: none;
}

.hero--intro .hero__intro > * {
  animation: hero-intro-rise 0.7s var(--constellation-ease-out) both;
}

.hero--intro .hero__intro > *:nth-child(1) { animation-delay: 0.05s; }
.hero--intro .hero__intro > *:nth-child(2) { animation-delay: 0.16s; }
.hero--intro .hero__intro > *:nth-child(3) { animation-delay: 0.28s; }
.hero--intro .hero__intro > *:nth-child(4) { animation-delay: 0.42s; }

@keyframes hero-intro-rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero__eyebrow {
  margin: 0;
  color: var(--color-accent);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.20em;
  text-transform: uppercase;
}

.hero__name {
  margin: 0;
  font-size: clamp(56px, 11vw, 128px);
  line-height: 0.96;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: var(--color-text);
}

.hero__lead {
  max-width: 540px;
  margin: 0;
  color: var(--color-muted);
  font-size: 16px;
  line-height: 1.5;
}

.hero__hint {
  margin: 18px 0 0;
  color: var(--color-muted-2);
  font-size: 12px;
  letter-spacing: 0.04em;
  opacity: 0.85;
}

/* Layout: sidebar + canvas, sitting flush against the topbar bottom border */
.hero__layout {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 0;
  transition: opacity 480ms var(--constellation-ease-out);
}

.hero--intro .hero__layout {
  opacity: 0;
  pointer-events: none;
}

/* Sidebar — surface continues from topbar (same backdrop blur, same dark wash) */
.hero__sidebar {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 18px 18px 22px;
  border-right: 1px solid var(--color-border);
  background: rgba(8, 9, 11, 0.62);
  backdrop-filter: blur(14px);
  overflow-y: auto;
}

.hero__sidebar-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.hero__sidebar-title {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.hero__sidebar-count {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-muted-2);
}

.hero__sidebar-group-title {
  margin: 0 0 6px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-muted-2);
}

.hero__sidebar-list {
  display: grid;
  gap: 4px;
  margin: 0 0 4px;
  padding: 0;
  list-style: none;
}

.hero__sidebar-item {
  display: grid;
  grid-template-columns: 8px 1fr auto;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 7px 10px;
  border: 1px solid transparent;
  border-radius: 3px;
  background: transparent;
  color: var(--color-text);
  font-family: inherit;
  font-size: 12px;
  text-align: left;
  cursor: pointer;
  transition: border-color 160ms var(--constellation-ease-out),
              background 160ms var(--constellation-ease-out);
}

.hero__sidebar-item:hover,
.hero__sidebar-item--hovered {
  border-color: var(--color-border);
  background: rgba(255, 255, 255, 0.03);
}

.hero__sidebar-item--top {
  border-color: var(--color-border-strong);
  background: rgba(0, 229, 255, 0.06);
}

.hero__sidebar-item:focus-visible {
  outline: 1px solid var(--color-accent);
  outline-offset: 1px;
}

.hero__sidebar-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
}

.hero__sidebar-dot--person { background: var(--color-text); border-color: var(--color-text); }
.hero__sidebar-dot--project { background: var(--color-accent); border-color: var(--color-accent); }
.hero__sidebar-dot--skill { background: transparent; border-style: dashed; border-color: rgba(0, 229, 255, 0.5); }
.hero__sidebar-dot--experience { background: transparent; border-color: rgba(255, 255, 255, 0.4); }
.hero__sidebar-dot--education { background: transparent; border-color: rgba(255, 255, 255, 0.28); }

.hero__sidebar-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hero__sidebar-score {
  font-size: 11px;
  color: var(--color-accent);
}

.hero__sidebar-stats {
  margin-top: auto;
  display: grid;
  gap: 6px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
}

.hero__sidebar-stat {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-muted);
}

.hero__sidebar-stat-key {
  letter-spacing: 0.04em;
}

.hero__sidebar-stat-value {
  color: var(--color-text);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.hero__sidebar-stat-value--accent {
  color: var(--color-accent);
}

/* Canvas: search + stage stacked */
.hero__canvas {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 0;
}

.hero__search-block {
  position: relative;
  z-index: 5;
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 22px 24px 14px;
}

.hero__error {
  width: min(640px, calc(100vw - 32px));
  margin: 0;
  padding: 9px 14px;
  border: 1px solid rgba(255, 92, 92, 0.32);
  border-radius: 3px;
  background: rgba(255, 92, 92, 0.08);
  color: rgba(255, 156, 156, 1);
  font-size: 12px;
  text-align: center;
}

.hero__mobile-loading {
  position: relative;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin: 16px auto;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 13px;
}

/* Stage */
.hero__stage {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.hero__edges {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.hero__edge {
  stroke: var(--color-edge);
  stroke-width: 1.2px;
  stroke-linecap: round;
  opacity: 0.32;
  transition: stroke 200ms var(--constellation-ease-out),
              opacity 200ms var(--constellation-ease-out),
              stroke-width 200ms var(--constellation-ease-out);
}

.hero__edge--top {
  stroke: var(--color-accent);
  stroke-width: 1.6px;
  opacity: 0.6;
}

.hero__edge--active {
  stroke: var(--color-accent);
  stroke-width: 1.8px;
  opacity: 0.85;
}

.hero__edge--dim {
  opacity: 0.06;
}

.hero__searching {
  position: absolute;
  left: 50%;
  top: 50%;
  z-index: 8;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 30px;
  padding: 0 14px;
  border: 1px solid var(--color-border-strong);
  border-radius: 3px;
  background: var(--color-surface-strong);
  color: var(--color-text);
  font-size: 12px;
  font-weight: 500;
  transform: translate(-50%, -50%);
  backdrop-filter: blur(14px);
}

.hero__searching-orbit {
  width: 13px;
  height: 13px;
  border: 1.5px solid rgba(255, 255, 255, 0.22);
  border-top-color: var(--color-accent);
  border-radius: 999px;
  animation: hero-orbit 800ms linear infinite;
}

@keyframes hero-orbit {
  to { transform: rotate(360deg); }
}

/* Hover card */
.hero__hover-card {
  position: absolute;
  z-index: 7;
  display: grid;
  gap: 4px;
  width: 240px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: rgba(8, 9, 11, 0.92);
  backdrop-filter: blur(14px);
  color: var(--color-text);
  pointer-events: none;
  transform: translate(70px, -50%);
  animation: hero-hover-card-in 200ms var(--constellation-ease-out) both;
}

.hero__hover-card-type {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.hero__hover-card-name {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: -0.005em;
}

.hero__hover-card-summary {
  font-size: 11px;
  line-height: 1.5;
  color: var(--color-muted);
}

.hero__hover-card-score {
  font-size: 10px;
  letter-spacing: 0.06em;
  color: var(--color-accent);
  margin-top: 2px;
}

@keyframes hero-hover-card-in {
  from { opacity: 0; transform: translate(70px, calc(-50% + 4px)); }
  to { opacity: 1; transform: translate(70px, -50%); }
}

@media (max-width: 1023px) {
  .hero__layout {
    grid-template-columns: 1fr;
  }

  .hero__sidebar {
    display: none;
  }
}

@media (max-width: 767px) {
  .hero__topbar {
    padding: 12px 16px;
  }

  .hero__brand-tagline,
  .hero__brand-divider {
    display: none;
  }

  .hero__search-block {
    padding: 12px 14px 8px;
  }

  .hero__name {
    font-size: clamp(48px, 14vw, 88px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero *,
  .hero--intro .hero__intro > * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
