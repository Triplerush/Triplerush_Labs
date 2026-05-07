import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { forceCenter, forceCollide, forceManyBody, forceSimulation, forceX, forceY } from 'd3-force'

const CENTRAL_POSITION = { x: 50, y: 48 }

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

const scoreRadius = (score, stageSize) => {
  const minDimension = Math.max(1, Math.min(stageSize.width, stageSize.height))
  if (typeof score !== 'number') return minDimension * 0.32
  return minDimension * (0.16 + (1 - clamp(score, 0, 1)) * 0.24)
}

const getStaticPosition = (node, index, total, stageSize) => {
  if (node.is_central) return CENTRAL_POSITION

  const angle = (-90 + index * (360 / Math.max(total, 1))) * (Math.PI / 180)
  const radius = scoreRadius(node.score, stageSize)
  const centerX = stageSize.width * 0.5
  const centerY = stageSize.height * 0.48

  return {
    x: ((centerX + Math.cos(angle) * radius) / stageSize.width) * 100,
    y: ((centerY + Math.sin(angle) * radius * 0.72) / stageSize.height) * 100,
  }
}

const createScoreWindForce = (stageSize) => {
  let simulationNodes = []

  const force = (alpha) => {
    const centerX = stageSize.value.width * 0.5
    const centerY = stageSize.value.height * 0.48

    simulationNodes.forEach((node) => {
      if (node.is_central || node.fx !== null || node.fy !== null) return

      const dx = node.x - centerX
      const dy = node.y - centerY
      const distance = Math.max(1, Math.hypot(dx, dy))
      const ux = dx / distance
      const uy = dy / distance
      const normalizedScore = typeof node.score === 'number' ? clamp(node.score, 0, 1) : 0.5
      const targetRadius = scoreRadius(node.score, stageSize.value)
      const radialDelta = targetRadius - distance
      const pullStrength = 0.006 + normalizedScore * 0.018
      const lowScoreWind = Math.max(0, 0.58 - normalizedScore) * 0.075
      const orbitWind = (0.5 - normalizedScore) * 0.018

      node.vx += ux * radialDelta * pullStrength * alpha
      node.vy += uy * radialDelta * pullStrength * alpha
      node.vx += ux * lowScoreWind * alpha
      node.vy += uy * lowScoreWind * alpha
      node.vx += -uy * orbitWind * alpha
      node.vy += ux * orbitWind * alpha
    })
  }

  force.initialize = (nodes) => {
    simulationNodes = nodes
  }

  return force
}

export function useConstellationPhysics({ nodes, stageSize, reducedMotion }) {
  const physicsNodes = shallowRef([])
  const positionMap = ref({})
  const trailPoints = ref([])
  const isCentralAgitated = ref(false)
  const simulation = shallowRef(null)
  let frameId = 0
  let draggedNodeId = ''
  let lastTrailTime = 0

  const centralPosition = computed(() => {
    const centralNode = physicsNodes.value.find((node) => node.is_central)
    if (!centralNode || !stageSize.value.width || !stageSize.value.height) return CENTRAL_POSITION
    return {
      x: (centralNode.x / stageSize.value.width) * 100,
      y: (centralNode.y / stageSize.value.height) * 100,
    }
  })

  const staticPositionMap = computed(() => {
    const map = {}
    const orbitNodes = nodes.value
      .filter((node) => !node.is_central)
      .sort((a, b) => {
        if (typeof a.score === 'number' || typeof b.score === 'number') return (b.score ?? -1) - (a.score ?? -1)
        return a.name.localeCompare(b.name)
      })

    nodes.value.forEach((node) => {
      if (node.is_central) map[node.id] = CENTRAL_POSITION
    })

    orbitNodes.forEach((node, index) => {
      map[node.id] = getStaticPosition(node, index, orbitNodes.length, stageSize.value)
    })

    return map
  })

  const getBoundaryPadding = () => stageSize.value.width < 760 ? 48 : 72

  const clampPhysicsNode = (node) => {
    const padding = Math.max(getBoundaryPadding(), node.radius || 48)
    node.x = clamp(node.x, padding, stageSize.value.width - padding)
    node.y = clamp(node.y, padding, stageSize.value.height - padding)
  }

  const getTrailColor = (node) => {
    const category = node.category || 'backend'
    if (category === 'person' || category === 'backend') return 'var(--color-brand-500)'
    if (category === 'ai-ml') return 'var(--color-accent-500)'
    if (category === 'infra') return 'var(--color-infra-500, oklch(0.70 0.15 200))'
    if (category === 'frontend') return 'var(--color-frontend-500, oklch(0.70 0.18 50))'
    return 'var(--color-brand-500)'
  }

  const updateTrails = () => {
    if (reducedMotion.value) {
      trailPoints.value = []
      return
    }

    const now = performance.now()
    const maxAge = 420
    const mobile = stageSize.value.width < 760
    const maxPerNode = mobile ? 4 : 8
    const nextTrailPoints = trailPoints.value
      .map((point) => ({ ...point, age: now - point.createdAt }))
      .filter((point) => point.age < maxAge)

    if (now - lastTrailTime > 70) {
      physicsNodes.value.forEach((node) => {
        if (node.is_central || typeof node.score !== 'number' || node.score < 0.45) return
        const speed = Math.hypot(node.vx || 0, node.vy || 0)
        if (speed < 0.35 && draggedNodeId !== node.id) return

        const countForNode = nextTrailPoints.filter((point) => point.nodeId === node.id).length
        if (countForNode >= maxPerNode) return

        nextTrailPoints.push({
          id: `${node.id}-${Math.round(now)}-${countForNode}`,
          nodeId: node.id,
          x: (node.x / stageSize.value.width) * 100,
          y: (node.y / stageSize.value.height) * 100,
          color: getTrailColor(node),
          createdAt: now,
          age: 0,
        })
      })
      lastTrailTime = now
    }

    trailPoints.value = nextTrailPoints.map((point) => ({
      ...point,
      opacity: Math.max(0, 1 - point.age / maxAge),
    }))
  }

  const commitPositions = () => {
    if (!stageSize.value.width || !stageSize.value.height) return

    const nextMap = {}
    physicsNodes.value.forEach((node) => {
      if (node.is_central) {
        node.x = stageSize.value.width * 0.5
        node.y = stageSize.value.height * 0.48
      } else {
        clampPhysicsNode(node)
      }

      nextMap[node.id] = {
        x: (node.x / stageSize.value.width) * 100,
        y: (node.y / stageSize.value.height) * 100,
      }
    })
    positionMap.value = nextMap
    updateTrails()

    const centralNode = physicsNodes.value.find((node) => node.is_central)
    isCentralAgitated.value = Boolean(centralNode && physicsNodes.value.some((node) => {
      if (node.is_central) return false
      const distance = Math.hypot(node.x - centralNode.x, node.y - centralNode.y)
      return distance < 150
    }))
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

  const rebuildSimulation = () => {
    stopSimulation()

    if (!stageSize.value.width || !stageSize.value.height) {
      positionMap.value = staticPositionMap.value
      return
    }

    if (reducedMotion.value) {
      physicsNodes.value = []
      positionMap.value = staticPositionMap.value
      trailPoints.value = []
      isCentralAgitated.value = false
      return
    }

    const staticMap = staticPositionMap.value
    const nextNodes = nodes.value.map((node) => {
      const previous = physicsNodes.value.find((candidate) => candidate.id === node.id)
      const fallback = staticMap[node.id] || CENTRAL_POSITION
      const x = previous?.x ?? (fallback.x / 100) * stageSize.value.width
      const y = previous?.y ?? (fallback.y / 100) * stageSize.value.height
      const radius = node.is_central ? 82 : node.type?.includes('experience') || node.type?.includes('education') ? 48 : 54
      const padding = Math.max(stageSize.value.width < 760 ? 48 : 72, radius)

      return {
        ...node,
        radius,
        x: clamp(x, padding, stageSize.value.width - padding),
        y: clamp(y, padding, stageSize.value.height - padding),
        fx: node.is_central ? stageSize.value.width * 0.5 : null,
        fy: node.is_central ? stageSize.value.height * 0.48 : null,
      }
    })

    physicsNodes.value = nextNodes
    simulation.value = forceSimulation(nextNodes)
      .alpha(0.94)
      .alphaDecay(0.018)
      .velocityDecay(0.34)
      .force('center', forceCenter(stageSize.value.width * 0.5, stageSize.value.height * 0.5).strength(0.04))
      .force('charge', forceManyBody().strength((node) => node.is_central ? -190 : -92))
      .force('collide', forceCollide().radius((node) => node.radius).strength(0.88).iterations(2))
      .force('x', forceX((node) => {
        if (node.is_central) return stageSize.value.width * 0.5
        return (staticMap[node.id]?.x ?? 50) / 100 * stageSize.value.width
      }).strength((node) => node.is_central ? 0.5 : 0.035))
      .force('y', forceY((node) => {
        if (node.is_central) return stageSize.value.height * 0.48
        return (staticMap[node.id]?.y ?? 50) / 100 * stageSize.value.height
      }).strength((node) => node.is_central ? 0.5 : 0.035))
      .force('scoreWind', createScoreWindForce(stageSize))
      .on('tick', scheduleCommit)

    commitPositions()
  }

  const stagePointFromEvent = (event) => {
    const rect = event.currentTarget.closest('.constellation-hero__stage')?.getBoundingClientRect()
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
  onBeforeUnmount(stopSimulation)

  return {
    centralPosition,
    positionMap,
    trailPoints,
    isCentralAgitated,
    startDrag,
    drag,
    endDrag,
    stopSimulation,
  }
}
