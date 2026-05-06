import { computed, ref } from 'vue'

const STORAGE_KEY = 'constellation:last-query'

const seedNodes = [
  {
    id: 'fernando-canal',
    type: 'person',
    name: 'Fernando Rubén Canal Mendoza',
    category: 'person',
    is_central: true,
    score: null,
    data: {
      role: 'AI Software Engineer',
      summary: 'Ingeniero de software especializado en backend, RAG, LLMs, MLOps y despliegue de aplicaciones inteligentes.',
      highlights: [
        'Sistemas RAG en producción con embeddings y recuperación vectorial.',
        'Backend en Python/FastAPI y Java/Spring Boot.',
        'Despliegue con Docker, Kubernetes, AWS y CI/CD.',
      ],
      contact: {
        email: 'fernandorcm9@gmail.com',
        linkedin: 'www.linkedin.com/in/fcanalm',
        location: 'Arequipa, Perú',
      },
    },
  },
  {
    id: 'experiencia-laboral',
    type: 'experience-bundle',
    name: 'Experiencia Laboral',
    category: 'backend',
    is_central: false,
    score: null,
    data: {
      summary: 'Trayectoria backend evolucionando hacia AI Engineering, arquitectura escalable y soluciones RAG.',
      highlights: [
        'PHAXSI: arquitectura modular, pipelines geoespaciales y pagos multimoneda.',
        'Anyone AI: liderazgo técnico en sistema RAG para pólizas.',
        'SmartPressure y freelance: APIs Spring Boot, PostgreSQL, Docker y testing.',
      ],
      stack: ['Python', 'FastAPI', 'Java', 'Spring Boot', 'LangChain', 'Docker'],
    },
  },
  {
    id: 'certificaciones-estudios',
    type: 'education-bundle',
    name: 'Certificaciones y Estudios',
    category: 'ai-ml',
    is_central: false,
    score: null,
    data: {
      summary: 'Formación en Ingeniería de Sistemas, AI/ML, agentes, aplicaciones LLM y DevOps multicloud.',
      highlights: [
        'Ingeniería de Sistemas - UNSA.',
        'Aprendizaje por refuerzo con Python.',
        'DevOps multicloud, agentes autónomos y aplicaciones basadas en LLMs.',
      ],
      stack: ['LLMs', 'Agentes autónomos', 'Docker', 'Kubernetes', 'Spring Boot'],
    },
  },
  {
    id: 'auto-profiling',
    type: 'project',
    name: 'Auto Profiling + AI Layer',
    category: 'backend',
    is_central: false,
    score: null,
    data: {
      description: 'Plataforma que visualiza análisis de datos como dashboards interactivos con agente AI integrado.',
      url: '/profiling/',
      status: 'live',
      highlights: [
        'Agente AI que explica dashboards en lenguaje natural.',
        'RAG sobre Data Contracts para búsqueda semántica.',
        'Model Service con predicciones y explicaciones LLM.',
      ],
      stack: ['FastAPI', 'Vue 3', 'LangChain', 'FAISS', 'Docker'],
    },
  },
]

const getInitialQuery = () => {
  try {
    return sessionStorage.getItem(STORAGE_KEY) || ''
  } catch {
    return ''
  }
}

const normalizeNode = (node) => ({
  ...node,
  data: node.data || {},
  is_central: Boolean(node.is_central),
  score: typeof node.score === 'number' ? node.score : null,
})

export function useConstellation() {
  const status = ref('idle')
  const query = ref(getInitialQuery())
  const nodes = ref(seedNodes)
  const selectedNode = ref(null)
  const errorMessage = ref('')
  const lastAnnouncement = ref('Constelación semántica lista.')

  const centralNode = computed(() => nodes.value.find((node) => node.is_central))

  const rankedNodes = computed(() => {
    return [...nodes.value].sort((a, b) => {
      if (a.is_central) return -1
      if (b.is_central) return 1
      return (b.score ?? -1) - (a.score ?? -1)
    })
  })

  const hasScores = computed(() => nodes.value.some((node) => typeof node.score === 'number'))

  const search = async (nextQuery = query.value) => {
    const cleanQuery = nextQuery.trim()
    query.value = cleanQuery

    if (!cleanQuery) {
      status.value = 'idle'
      errorMessage.value = ''
      return
    }

    try {
      sessionStorage.setItem(STORAGE_KEY, cleanQuery)
    } catch {
      // sessionStorage can be unavailable in private or restricted contexts.
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
      nodes.value = Array.isArray(payload) ? payload.map(normalizeNode) : seedNodes
      status.value = 'results'
      updateAnnouncement()
    } catch (error) {
      nodes.value = seedNodes
      selectedNode.value = null
      status.value = 'error'
      errorMessage.value = error.message || 'El backend semántico no está disponible. Puedes ver el portfolio clásico.'
      lastAnnouncement.value = `No se pudo completar la búsqueda. ${errorMessage.value}`
    }
  }

  const expandNode = (node) => {
    selectedNode.value = node
    status.value = 'expanded'
  }

  const closeDetail = () => {
    selectedNode.value = null
    status.value = hasScores.value ? 'results' : 'idle'
  }

  const clearSearch = () => {
    query.value = ''
    nodes.value = seedNodes
    selectedNode.value = null
    errorMessage.value = ''
    status.value = 'idle'
    lastAnnouncement.value = 'Búsqueda limpiada. Constelación en reposo.'
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      // Ignore storage failures.
    }
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
    search,
    expandNode,
    closeDetail,
    clearSearch,
  }
}
