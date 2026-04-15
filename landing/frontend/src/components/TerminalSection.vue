<template>
  <section class="py-24 sm:py-32">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="section-animate rounded-2xl overflow-hidden border"
           :class="theme === 'dark' ? 'border-white/10' : 'border-black/10'">
        <!-- Title bar -->
        <div class="flex items-center gap-2 px-4 py-3 border-b"
             :class="theme === 'dark' ? 'bg-[#161b22] border-white/5' : 'bg-gray-100 border-black/5'">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
          <span class="ml-2 text-xs opacity-40 font-mono">fernando@portfolio:~</span>
        </div>
        <!-- Terminal content -->
        <div class="p-6 font-mono text-sm min-h-[220px] leading-relaxed"
             :class="theme === 'dark' ? 'bg-[#0d1117] text-green-400' : 'bg-gray-950 text-green-400'">
          <div v-for="(line, i) in visibleLines" :key="i" class="mb-0.5">
            <template v-if="line.type === 'command'">
              <span class="text-brand-400">$ </span>
              <span class="text-white">{{ line.text }}</span>
            </template>
            <template v-else-if="line.type === 'output'">
              <span class="opacity-70">{{ line.text }}</span>
            </template>
            <template v-else-if="line.type === 'highlight'">
              <span class="text-accent-400">{{ line.text }}</span>
            </template>
            <template v-else>
              <span>&nbsp;</span>
            </template>
          </div>
          <span v-if="showCursor" class="inline-block w-2 h-4 bg-green-400 animate-pulse ml-0.5"></span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, inject, onMounted, onBeforeUnmount } from 'vue'

const theme = inject('theme')
const visibleLines = ref([])
const showCursor = ref(true)
let currentIndex = 0
let timer = null
let observer = null
let started = false

const lines = [
  { type: 'command', text: 'cat about.md' },
  { type: 'output', text: 'Fernando Canal — AI Software Engineer' },
  { type: 'output', text: 'Backend & ML en produccion, no solo notebooks.' },
  { type: 'blank' },
  { type: 'command', text: 'ls skills/' },
  { type: 'highlight', text: 'RAG/  Agents/  FastAPI/  Docker/  MLOps/  Vue3/' },
  { type: 'blank' },
  { type: 'command', text: 'git log --oneline -3' },
  { type: 'output', text: 'c46f6fd  fix(docker): marcar portfolio-net como red externa' },
  { type: 'output', text: '7070a63  feat(ci/cd): integrar despliegue con GHCR' },
  { type: 'output', text: '5894120  refactor(landing): estabilizar modelos RAG' },
  { type: 'blank' },
  { type: 'command', text: 'echo $STATUS' },
  { type: 'highlight', text: 'Abierto a oportunidades  ✓' },
]

function typeNextLine() {
  if (currentIndex < lines.length) {
    visibleLines.value.push(lines[currentIndex])
    currentIndex++
    const delay = lines[currentIndex - 1].type === 'command' ? 600 : 150
    timer = setTimeout(typeNextLine, delay)
  }
}

onMounted(() => {
  const section = document.querySelector('#terminal-section')
  if (!section) return

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting && !started) {
        started = true
        timer = setTimeout(typeNextLine, 400)
      }
    },
    { threshold: 0.3 }
  )
  observer.observe(section)
})

onBeforeUnmount(() => {
  if (timer) clearTimeout(timer)
  if (observer) observer.disconnect()
})
</script>
