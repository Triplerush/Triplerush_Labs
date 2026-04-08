<template>
  <section id="skills" class="py-24 sm:py-32">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="section-animate text-center mb-16">
        <span class="inline-block text-xs font-semibold tracking-[0.2em] uppercase mb-4 opacity-50">Stack</span>
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
          Technical <span class="gradient-text">Skills</span>
        </h2>
        <p class="text-base sm:text-lg max-w-2xl mx-auto opacity-60">
          A blend of AI/ML, backend engineering, and infrastructure — the full stack for shipping intelligent systems.
        </p>
      </div>

      <!-- Skills categories -->
      <div class="grid sm:grid-cols-2 gap-6 stagger-children">
        <div v-for="category in categories" :key="category.name"
             class="glass-card rounded-2xl p-6 sm:p-8"
             :id="'skills-' + category.id">
          <!-- Category header -->
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
                 :style="{ background: `linear-gradient(135deg, ${category.colorFrom}, ${category.colorTo})` }">
              {{ category.icon }}
            </div>
            <h3 class="text-lg font-bold">{{ category.name }}</h3>
          </div>

          <!-- Skills badges -->
          <div class="flex flex-wrap gap-2">
            <span v-for="skill in category.skills" :key="skill"
                  class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 cursor-default hover:scale-105"
                  :class="theme === 'dark'
                    ? 'bg-white/5 hover:bg-white/10 text-white/80'
                    : 'bg-black/5 hover:bg-black/10 text-black/70'"
                  :style="{ '--tw-ring-color': category.colorFrom }"
                  @mouseenter="$event.target.style.boxShadow = `0 0 0 1px ${category.colorFrom}40`"
                  @mouseleave="$event.target.style.boxShadow = 'none'">
              {{ skill }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { inject } from 'vue'

const theme = inject('theme')

const categories = [
  {
    id: 'ai-ml',
    name: 'AI / Machine Learning',
    icon: '🧠',
    colorFrom: '#8b5cf6',
    colorTo: '#a855f7',
    skills: [
      'RAG Systems', 'LangChain', 'PyTorch', 'TensorFlow',
      'FAISS', 'ChromaDB', 'Fine-tuning (LoRA/QLoRA)',
      'Sentence Transformers', 'OpenSearch', 'Hugging Face',
    ],
  },
  {
    id: 'backend',
    name: 'Backend Engineering',
    icon: '⚙️',
    colorFrom: '#3b82f6',
    colorTo: '#6366f1',
    skills: [
      'FastAPI', 'Spring Boot', 'Python', 'Java',
      'PostgreSQL', 'REST APIs', 'WebSockets',
      'Alembic', 'Flyway', 'SQLAlchemy',
    ],
  },
  {
    id: 'infra',
    name: 'Infrastructure & MLOps',
    icon: '🚀',
    colorFrom: '#10b981',
    colorTo: '#06b6d4',
    skills: [
      'Docker', 'Kubernetes', 'GitHub Actions', 'Jenkins',
      'Terraform', 'CI/CD', 'SonarQube', 'Nginx',
      'MLflow', 'Linux',
    ],
  },
  {
    id: 'frontend',
    name: 'Frontend & Visualization',
    icon: '🎨',
    colorFrom: '#f59e0b',
    colorTo: '#ef4444',
    skills: [
      'Vue 3', 'Tailwind CSS', 'Chart.js', 'Vite',
      'Responsive Design', 'Composition API',
    ],
  },
]
</script>
