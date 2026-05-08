<template>
  <div class="app dark">
    <ConstellationHero />
    <ChatWidget />
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import ChatWidget from './components/ChatWidget.vue'
import ConstellationHero from './components/ConstellationHero.vue'

const projects = ref([])
const theme = ref('dark')

provide('theme', theme)
provide('projects', projects)

onMounted(async () => {
  document.body.className = 'dark'

  try {
    const res = await fetch('/v1/projects')
    if (res.ok) {
      const all = await res.json()
      projects.value = all.filter((project) => project.status === 'live')
    }
  } catch {
    // Backend unavailable — chat chips silently skip
  }
})
</script>

<style scoped>
.app {
  min-height: 100dvh;
  background: var(--color-bg);
  color: var(--color-text);
}
</style>
