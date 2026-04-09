<template>
  <section id="projects" class="py-24 sm:py-32">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="section-animate text-center mb-16">
        <span class="inline-block text-xs font-semibold tracking-[0.2em] uppercase mb-4 opacity-50">Portfolio</span>
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
          Proyectos <span class="gradient-text">Destacados</span>
        </h2>
        <p class="text-base sm:text-lg max-w-2xl mx-auto opacity-60">
          Aplicaciones de IA desplegadas en produccion - no solo notebooks.
        </p>
      </div>

      <!-- Projects grid -->
      <div class="grid gap-6 md:gap-8 stagger-children">
        <article v-for="project in projects" :key="project.id"
                 class="glass-card rounded-2xl overflow-hidden group cursor-pointer"
                 :id="'project-' + project.id">
          <div class="p-6 sm:p-8">
            <!-- Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-xl sm:text-2xl font-bold group-hover:text-brand-400 transition-colors">
                    {{ project.name }}
                  </h3>
                  <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold"
                        :class="statusClasses(project.status)">
                    <span class="w-1.5 h-1.5 rounded-full"
                          :class="project.status === 'live' ? 'bg-green-400' : 'bg-yellow-400'"></span>
                    {{ project.status === 'live' ? 'LIVE' : 'WIP' }}
                  </span>
                </div>
                <p class="text-sm sm:text-base opacity-60 leading-relaxed">
                  {{ project.description }}
                </p>
              </div>
              <a v-if="project.url" :href="project.url" 
                 class="ml-4 p-2 rounded-lg opacity-40 group-hover:opacity-100 hover:bg-white/10 transition-all flex-shrink-0"
                 :id="'project-link-' + project.id"
                 :title="'Open ' + project.name">
                <svg class="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>

            <!-- Highlights (visible on hover / always on mobile) -->
            <div class="mb-5 space-y-2 max-h-0 md:max-h-0 md:group-hover:max-h-40 overflow-hidden transition-all duration-500 max-sm:max-h-40">
              <div v-for="(highlight, i) in project.highlights" :key="i"
                   class="flex items-start gap-2 text-sm opacity-70">
                <svg class="w-4 h-4 text-brand-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4" />
                </svg>
                <span>{{ highlight }}</span>
              </div>
            </div>

            <!-- Tech stack -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span v-for="tech in project.stack" :key="tech"
                    class="px-2.5 py-1 rounded-lg text-xs font-medium transition-colors"
                    :class="theme === 'dark' 
                      ? 'bg-white/5 text-white/70 group-hover:bg-brand-500/15 group-hover:text-brand-300' 
                      : 'bg-black/5 text-black/60 group-hover:bg-brand-500/10 group-hover:text-brand-700'">
                {{ tech }}
              </span>
            </div>

            <!-- Demonstrates badges -->
            <div class="flex flex-wrap gap-2">
              <span v-for="demo in project.demonstrates" :key="demo"
                    class="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase"
                    :class="theme === 'dark' 
                      ? 'text-accent-400/80 bg-accent-500/10' 
                      : 'text-accent-600 bg-accent-500/10'">
                {{ demo }}
              </span>
            </div>
          </div>
        </article>
      </div>

      <!-- More coming soon -->
      <div class="section-animate mt-12 text-center">
        <div class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-dashed opacity-40"
             :class="theme === 'dark' ? 'border-white/20' : 'border-black/20'">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-sm font-medium">Mas proyectos proximamente</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { inject } from 'vue'

const theme = inject('theme')

defineProps({
  projects: {
    type: Array,
    required: true,
  },
})

const statusClasses = (status) => {
  if (status === 'live') {
    return 'bg-green-500/15 text-green-400'
  }
  return 'bg-yellow-500/15 text-yellow-400'
}
</script>
