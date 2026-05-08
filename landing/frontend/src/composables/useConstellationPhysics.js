import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
} from 'd3-force'

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

// Node radii (in px). Central is slightly larger than the others.
// These match the visual diameters in ConstellationNode.vue (124 / 104).
const NODE_RADIUS = {
  person: 62,
  skill: 52,
  experience: 52,
  project: 52,
  education: 52,
}

const radiusFor = (node) => NODE_RADIUS[node.type] || 50

const buildEdges = (nodesList) => {
  const seen = new Set()
  const edges = []
  const idSet = new Set(nodesList.map((node) => node.id))

  for (const node of nodesList) {
    const connections = node.data?.connections || node.connections || []
    for (const targetId of connections) {
      if (!idSet.has(targetId) || targetId === node.id) continue
      const key = node.id < targetId ? `${node.id}|${targetId}` : `${targetId}|${node.id}`
      if (seen.has(key)) continue
      seen.add(key)
      edges.push({ source: node.id, target: targetId })
    }
  }

  return edges
}

// Assign each non-central node a fixed angular slot around the central node so
// the orbit ring is evenly distributed regardless of link clustering.
const computeAngularSlots = (nodesList) => {
  const orbitNodes = nodesList.filter((n) => !n.is_central)
  const slots = {}
  const total = orbitNodes.length
  if (!total) return slots

  // Stable slot order — sort by id so initial positions don't shuffle on each
  // refetch. Start angle at -90deg so the first node sits straight up.
  const sorted = [...orbitNodes].sort((a, b) => a.id.localeCompare(b.id))
  sorted.forEach((node, idx) => {
    slots[node.id] = -Math.PI / 2 + (idx / total) * Math.PI * 2
  })
  return slots
}

const orbitRadius = (stageSize) => {
  const minDim = Math.min(stageSize.width, stageSize.height)
  // Larger graphs get more breathing room; clamp to keep things reasonable.
  return clamp(minDim * 0.34, 180, 320)
}

const scoreOffset = (score, baseRadius) => {
  // During search, top scorers drift inward, low scorers drift outward.
  if (typeof score !== 'number') return baseRadius
  const normalized = clamp(score, 0, 1)
  // 0.0 → +30% (push out); 1.0 → -25% (pull in)
  return baseRadius * (1 + (0.3 - normalized * 0.55))
}

export function useConstellationPhysics({ nodes, stageSize, reducedMotion, searchActive }) {
  const physicsNodes = shallowRef([])
  const positionMap = ref({})
  const edges = shallowRef([])
  const simulation = shallowRef(null)
  let frameId = 0
  let draggedNodeId = ''

  const centralPosition = computed(() => {
    const central = physicsNodes.value.find((node) => node.is_central)
    if (!central || !stageSize.value.width) return { x: 50, y: 50 }
    return {
      x: (central.x / stageSize.value.width) * 100,
      y: (central.y / stageSize.value.height) * 100,
    }
  })

  const edgeMap = computed(() => {
    const map = new Map()
    for (const edge of edges.value) {
      const source = typeof edge.source === 'string' ? edge.source : edge.source.id
      const target = typeof edge.target === 'string' ? edge.target : edge.target.id
      if (!map.has(source)) map.set(source, new Set())
      if (!map.has(target)) map.set(target, new Set())
      map.get(source).add(target)
      map.get(target).add(source)
    }
    return map
  })

  const connectedIds = (nodeId) => edgeMap.value.get(nodeId) || new Set()

  const getBoundaryPadding = () => stageSize.value.width < 768 ? 64 : 96

  const clampPhysicsNode = (node) => {
    const padding = Math.max(getBoundaryPadding(), node.radius || 50)
    node.x = clamp(node.x, padding, stageSize.value.width - padding)
    node.y = clamp(node.y, padding, stageSize.value.height - padding)
  }

  const commitPositions = () => {
    if (!stageSize.value.width || !stageSize.value.height) return

    const next = {}
    physicsNodes.value.forEach((node) => {
      clampPhysicsNode(node)
      next[node.id] = {
        x: (node.x / stageSize.value.width) * 100,
        y: (node.y / stageSize.value.height) * 100,
      }
    })
    positionMap.value = next
  }

  const scheduleCommit = () => {
    if (frameId) return
    frameId = requestAnimationFrame(() => {
      frameId = 0
      commitPositions()
    })
  }

  const stopSimulation = () => {
    simulation.value?.stop()
    simulation.value = null
    if (frameId) {
      cancelAnimationFrame(frameId)
      frameId = 0
    }
  }

  const targetPositionFor = (node, slots, baseRadius, stageMid) => {
    if (node.is_central) return { x: stageMid.cx, y: stageMid.cy }
    const angle = slots[node.id] ?? 0
    const radius = searchActive.value ? scoreOffset(node.score, baseRadius) : baseRadius
    return {
      x: stageMid.cx + Math.cos(angle) * radius,
      y: stageMid.cy + Math.sin(angle) * radius,
    }
  }

  const rebuildSimulation = () => {
    stopSimulation()

    if (!stageSize.value.width || !stageSize.value.height) return

    const cx = stageSize.value.width * 0.5
    const cy = stageSize.value.height * 0.5
    const stageMid = { cx, cy }
    const slots = computeAngularSlots(nodes.value)
    const baseRadius = orbitRadius(stageSize.value)

    if (reducedMotion.value) {
      const nextPositions = {}
      nodes.value.forEach((node) => {
        const target = targetPositionFor(node, slots, baseRadius, stageMid)
        nextPositions[node.id] = {
          x: (target.x / stageSize.value.width) * 100,
          y: (target.y / stageSize.value.height) * 100,
        }
      })
      physicsNodes.value = []
      edges.value = buildEdges(nodes.value)
      positionMap.value = nextPositions
      return
    }

    const previousById = new Map(physicsNodes.value.map((node) => [node.id, node]))
    const nextNodes = nodes.value.map((node) => {
      const previous = previousById.get(node.id)
      const target = targetPositionFor(node, slots, baseRadius, stageMid)
      const radius = radiusFor(node)
      const isCentral = Boolean(node.is_central)
      return {
        ...node,
        radius,
        slot: slots[node.id] ?? null,
        x: previous?.x ?? target.x,
        y: previous?.y ?? target.y,
        vx: previous?.vx ?? 0,
        vy: previous?.vy ?? 0,
        fx: isCentral ? cx : null,
        fy: isCentral ? cy : null,
      }
    })

    const nextEdges = buildEdges(nextNodes)
    physicsNodes.value = nextNodes
    edges.value = nextEdges

    simulation.value = forceSimulation(nextNodes)
      .alpha(0.92)
      .alphaDecay(0.026)
      .velocityDecay(0.42)
      // Light link force just to add a hint of pull between connected pairs
      // — not strong enough to override the angular layout.
      .force('link', forceLink(nextEdges)
        .id((node) => node.id)
        .distance(baseRadius)
        .strength(0.06))
      .force('charge', forceManyBody().strength((node) => node.is_central ? -200 : -120))
      .force('collide', forceCollide().radius((node) => node.radius + 12).strength(0.96).iterations(2))
      .force('center', forceCenter(cx, cy).strength(0.04))
      // Strong target pull so each node sits at its angular slot.
      .force('targetX', forceX((node) => {
        if (node.is_central) return cx
        return targetPositionFor(node, slots, baseRadius, stageMid).x
      }).strength((node) => node.is_central ? 1 : 0.32))
      .force('targetY', forceY((node) => {
        if (node.is_central) return cy
        return targetPositionFor(node, slots, baseRadius, stageMid).y
      }).strength((node) => node.is_central ? 1 : 0.32))
      .on('tick', scheduleCommit)

    commitPositions()
  }

  const stagePointFromEvent = (event) => {
    const rect = event.currentTarget.closest('.hero__stage')?.getBoundingClientRect()
    if (!rect) return null
    const padding = getBoundaryPadding()
    return {
      x: clamp(event.clientX - rect.left, padding, rect.width - padding),
      y: clamp(event.clientY - rect.top, padding, rect.height - padding),
    }
  }

  const startDrag = (node, event) => {
    if (reducedMotion.value || node.is_central) return
    const physicsNode = physicsNodes.value.find((candidate) => candidate.id === node.id)
    const point = stagePointFromEvent(event)
    if (!physicsNode || !point) return

    draggedNodeId = node.id
    physicsNode.fx = point.x
    physicsNode.fy = point.y
    simulation.value?.alphaTarget(0.24).restart()
  }

  const drag = (event) => {
    if (!draggedNodeId || reducedMotion.value) return
    const physicsNode = physicsNodes.value.find((candidate) => candidate.id === draggedNodeId)
    const point = stagePointFromEvent(event)
    if (!physicsNode || !point) return

    physicsNode.fx = point.x
    physicsNode.fy = point.y
    commitPositions()
  }

  const endDrag = () => {
    if (!draggedNodeId) return
    const physicsNode = physicsNodes.value.find((candidate) => candidate.id === draggedNodeId)
    if (physicsNode) {
      physicsNode.fx = null
      physicsNode.fy = null
    }
    draggedNodeId = ''
    simulation.value?.alphaTarget(0).restart()
  }

  watch([nodes, stageSize, reducedMotion], rebuildSimulation, { immediate: true, deep: true })
  watch(searchActive, () => {
    if (!simulation.value) return
    simulation.value.alpha(0.55).restart()
  })

  onBeforeUnmount(stopSimulation)

  return {
    centralPosition,
    positionMap,
    edges,
    edgeMap,
    connectedIds,
    nodeRadii: computed(() => {
      const map = {}
      physicsNodes.value.forEach((node) => { map[node.id] = node.radius })
      return map
    }),
    startDrag,
    drag,
    endDrag,
    stopSimulation,
  }
}
