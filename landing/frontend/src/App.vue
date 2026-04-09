<template>
  <div :class="theme" class="min-h-screen transition-colors duration-300">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 border-b backdrop-blur-xl transition-all duration-300"
         :class="navClasses">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <a href="#" class="text-lg font-bold gradient-text" id="nav-logo">
            fernando.dev
          </a>
          <div class="hidden md:flex items-center gap-8">
            <a v-for="link in navLinks" :key="link.href" :href="link.href"
               class="text-sm font-medium opacity-70 hover:opacity-100 transition-opacity duration-200"
               :id="'nav-' + link.id">
              {{ link.label }}
            </a>
          </div>
          <div class="flex items-center gap-3">
            <ThemeToggle :theme="theme" @toggle="toggleTheme" />
            <button @click="mobileMenuOpen = !mobileMenuOpen" 
                    class="md:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
                    id="mobile-menu-btn"
                    aria-label="Toggle mobile menu">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <!-- Mobile menu -->
        <transition name="slide-down">
          <div v-if="mobileMenuOpen" class="md:hidden pb-4 space-y-2">
            <a v-for="link in navLinks" :key="link.href" :href="link.href"
               @click="mobileMenuOpen = false"
               class="block px-3 py-2 rounded-lg text-sm font-medium opacity-70 hover:opacity-100 hover:bg-white/5 transition-all">
              {{ link.label }}
            </a>
          </div>
        </transition>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <HeroSection />
      <ProjectsGrid :projects="projects" />
      <SkillsBadges />
      <AboutMe />
      <ContactSection />
    </main>

    <!-- Footer -->
    <footer class="border-t py-8 text-center text-sm opacity-50 transition-colors"
            :class="theme === 'dark' ? 'border-white/10' : 'border-black/10'">
      <div class="max-w-6xl mx-auto px-4">
        <p>&copy; {{ currentYear }} Fernando. Construido con Vue 3 + Tailwind CSS v4.</p>
      </div>
    </footer>

    <!-- Chat Widget (Fase 3 — AI Chatbot) -->
    <ChatWidget />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, provide } from 'vue'
import HeroSection from './components/HeroSection.vue'
import ProjectsGrid from './components/ProjectsGrid.vue'
import SkillsBadges from './components/SkillsBadges.vue'
import AboutMe from './components/AboutMe.vue'
import ContactSection from './components/ContactSection.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import ChatWidget from './components/ChatWidget.vue'

const theme = ref('dark')
const mobileMenuOpen = ref(false)
const currentYear = new Date().getFullYear()
const projects = ref([])

const navLinks = [
  { id: 'projects', href: '#projects', label: 'Proyectos' },
  { id: 'skills', href: '#skills', label: 'Skills' },
  { id: 'about', href: '#about', label: 'Sobre Mi' },
  { id: 'contact', href: '#contact', label: 'Contacto' },
]

const navClasses = computed(() => {
  return theme.value === 'dark'
    ? 'bg-surface-900/80 border-white/10'
    : 'bg-white/80 border-black/10'
})

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  document.body.className = theme.value
  localStorage.setItem('theme', theme.value)
}

provide('theme', theme)

onMounted(async () => {
  const savedTheme = localStorage.getItem('theme') || 'dark'
  theme.value = savedTheme
  document.body.className = savedTheme

  // Fetch projects from backend (single source of truth)
  try {
    const res = await fetch('/v1/projects')
    if (res.ok) {
      projects.value = await res.json()
    }
  } catch {
    // Backend unavailable — projects section stays empty
  }

  // Intersection Observer for scroll animations
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
        }
      })
    },
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
  )

  document.querySelectorAll('.section-animate, .stagger-children').forEach((el) => {
    observer.observe(el)
  })
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
