import { computed, onMounted, ref } from 'vue'

const fallbackNodes = [
  {
    id: 'fernando-canal',
    type: 'person',
    name: 'Fernando Canal',
    category: 'person',
    is_central: true,
    score: null,
    data: {
      role: 'AI Software Engineer',
      summary: 'Ingeniero de software backend evolucionando hacia AI Engineering.',
      connections: ['experience', 'education', 'skills'],
    },
  },
  {
    id: 'experience',
    type: 'experience',
    name: 'Experiencia',
    category: 'experience',
    is_central: false,
    score: null,
    data: {
      summary: 'Trayectoria backend evolucionando hacia AI Engineering.',
      connections: ['fernando-canal'],
    },
  },
  {
    id: 'education',
    type: 'education',
    name: 'Formación',
    category: 'education',
    is_central: false,
    score: null,
    data: {
      summary: 'Educación formal en Ingeniería de Sistemas y certificaciones en AI/ML.',
      connections: ['fernando-canal'],
    },
  },
  {
    id: 'skills',
    type: 'skill',
    name: 'Skills',
    category: 'skill',
    is_central: false,
    score: null,
    data: {
      summary: 'AI/ML, backend, MLOps y frontend.',
      connections: ['fernando-canal'],
    },
  },
]

const normalizeNode = (node) => ({
  ...node,
  data: node.data || {},
  is_central: Boolean(node.is_central),
  score: typeof node.score === 'number' ? node.score : null,
})

export function useConstellation() {
  const status = ref('loading')
  const query = ref('')
  const nodes = ref(fallbackNodes)
  const selectedNode = ref(null)
  const errorMessage = ref('')
  const lastAnnouncement = ref('Cargando constelación semántica.')

  const centralNode = computed(() => nodes.value.find((node) => node.is_central))

  const rankedNodes = computed(() => {
    return [...nodes.value].sort((a, b) => {
      if (a.is_central) return -1
      if (b.is_central) return 1
      return (b.score ?? -1) - (a.score ?? -1)
    })
  })

  const hasScores = computed(() => nodes.value.some((node) => typeof node.score === 'number'))
  const searchActive = computed(() => status.value === 'results' || status.value === 'expanded')

  const loadConstellation = async () => {
    try {
      const response = await fetch('/v1/constellation')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const payload = await response.json()
      if (Array.isArray(payload) && payload.length) {
        nodes.value = payload.map(normalizeNode)
      }
      status.value = 'idle'
      lastAnnouncement.value = `Constelación cargada con ${nodes.value.length} nodos.`
    } catch {
      status.value = 'idle'
      lastAnnouncement.value = 'Constelación en modo local (backend no disponible).'
    }
  }

  const search = async (nextQuery = query.value) => {
    const cleanQuery = nextQuery.trim()
    query.value = cleanQuery

    if (!cleanQuery) {
      status.value = hasScores.value ? 'results' : 'idle'
      errorMessage.value = ''
      return
    }

    status.value = 'searching'
    errorMessage.value = ''

    try {
      const response = await fetch('/v1/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: cleanQuery }),
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        const detail = payload?.detail
        const message = typeof detail === 'string' ? detail : detail?.message || payload?.message
        throw new Error(message || `No se pudo buscar la constelación (${response.status}).`)
      }

      const payload = await response.json()
      if (Array.isArray(payload)) {
        nodes.value = payload.map(normalizeNode)
      }
      status.value = 'results'
      updateAnnouncement()
    } catch (error) {
      status.value = 'error'
      errorMessage.value = error.message || 'El backend semántico no está disponible.'
      lastAnnouncement.value = `No se pudo completar la búsqueda. ${errorMessage.value}`
    }
  }

  const expandNode = (node) => {
    selectedNode.value = node
    status.value = 'expanded'
  }

  const focusNodeById = (nodeId) => {
    const target = nodes.value.find((node) => node.id === nodeId)
    if (target) expandNode(target)
  }

  const closeDetail = () => {
    selectedNode.value = null
    status.value = hasScores.value ? 'results' : 'idle'
  }

  const clearSearch = () => {
    query.value = ''
    nodes.value = nodes.value.map((node) => ({ ...node, score: null }))
    selectedNode.value = null
    errorMessage.value = ''
    status.value = 'idle'
    lastAnnouncement.value = 'Búsqueda limpiada. Constelación en reposo.'
  }

  const updateAnnouncement = () => {
    const scored = nodes.value
      .filter((node) => typeof node.score === 'number')
      .sort((a, b) => b.score - a.score)

    if (!scored.length) {
      lastAnnouncement.value = 'Búsqueda completada sin resultados puntuados.'
      return
    }

    const [best, ...others] = scored
    const otherNames = others.slice(0, 2).map((node) => node.name).join(', ')
    lastAnnouncement.value = `Búsqueda completada. ${scored.length} resultados. Mejor coincidencia: ${best.name} con score ${best.score.toFixed(2)}.${otherNames ? ` Otros relevantes: ${otherNames}.` : ''}`
  }

  onMounted(loadConstellation)

  return {
    status,
    query,
    nodes,
    rankedNodes,
    centralNode,
    selectedNode,
    errorMessage,
    lastAnnouncement,
    hasScores,
    searchActive,
    search,
    expandNode,
    focusNodeById,
    closeDetail,
    clearSearch,
  }
}
