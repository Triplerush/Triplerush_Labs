<template>
  <section id="about" class="py-24 sm:py-32">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="section-animate text-center mb-16">
        <span class="inline-block text-xs font-semibold tracking-[0.2em] uppercase mb-4 opacity-50">Background</span>
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
          About <span class="gradient-text">Me</span>
        </h2>
      </div>

      <div class="grid lg:grid-cols-5 gap-8 lg:gap-12">
        <!-- Bio column -->
        <div class="lg:col-span-3 section-animate">
          <div class="glass-card rounded-2xl p-6 sm:p-8 hover:translate-y-0">
            <h3 class="text-xl font-bold mb-4">
              🎯 AI Engineer with a Backend DNA
            </h3>
            <div class="space-y-4 text-sm sm:text-base opacity-75 leading-relaxed">
              <p>
                I'm Fernando — an <strong class="opacity-100">AI Software Engineer</strong> focused on 
                building intelligent systems that actually work in production, not just in notebooks.
              </p>
              <p>
                My path is unconventional: I started in <strong class="opacity-100">Backend Engineering</strong> 
                (Java/Spring Boot, Python/FastAPI) and evolved toward AI — bringing software engineering 
                discipline to the world of ML. I build <strong class="opacity-100">RAG pipelines</strong>, 
                orchestrate <strong class="opacity-100">LLM agents</strong>, and deploy them with proper 
                CI/CD, monitoring, and infrastructure.
              </p>
              <p>
                My unique value? I bridge the gap between the AI researcher who creates a model 
                and the infrastructure needed to scale it. From <strong class="opacity-100">semantic search 
                with FAISS/OpenSearch</strong> to <strong class="opacity-100">Docker/Kubernetes deployments</strong>,
                I own the full lifecycle.
              </p>
              <p>
                Currently deepening my expertise in <strong class="opacity-100">Reinforcement Learning</strong> 
                (the foundation of RLHF for LLM alignment) and <strong class="opacity-100">DevOps/MLOps</strong> 
                (Docker, K8s, Terraform, CI/CD pipelines).
              </p>
            </div>
          </div>
        </div>

        <!-- Career Roadmap column -->
        <div class="lg:col-span-2 section-animate" style="animation-delay: 0.2s;">
          <div class="glass-card rounded-2xl p-6 sm:p-8 hover:translate-y-0">
            <h3 class="text-xl font-bold mb-6">
              🗺️ Career Roadmap
            </h3>
            
            <div class="relative">
              <!-- Vertical line -->
              <div class="absolute left-4 top-6 bottom-6 w-0.5 rounded-full"
                   style="background: linear-gradient(to bottom, var(--color-brand-500), var(--color-accent-500), var(--color-surface-700));">
              </div>

              <!-- Phase items -->
              <div v-for="(phase, index) in phases" :key="phase.label"
                   class="relative pl-12 pb-8 last:pb-0">
                <!-- Dot -->
                <div class="absolute left-2.5 top-1 w-3 h-3 rounded-full border-2"
                     :class="phase.active 
                       ? 'bg-brand-500 border-brand-400 shadow-[0_0_8px_var(--color-brand-500)]' 
                       : theme === 'dark' ? 'bg-surface-700 border-surface-600' : 'bg-gray-200 border-gray-300'">
                </div>

                <!-- Content -->
                <div>
                  <span class="text-[10px] font-bold tracking-wider uppercase"
                        :class="phase.active ? 'text-brand-400' : 'opacity-40'">
                    {{ phase.timeline }}
                  </span>
                  <h4 class="text-sm font-bold mt-1" :class="{ 'opacity-50': !phase.active }">
                    {{ phase.title }}
                  </h4>
                  <p class="text-xs mt-1 opacity-50">
                    {{ phase.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Currently learning -->
          <div class="glass-card rounded-2xl p-6 mt-6 hover:translate-y-0">
            <h4 class="text-sm font-bold mb-3 opacity-70">📚 Currently Learning</h4>
            <ul class="space-y-2 text-xs opacity-60">
              <li class="flex items-start gap-2">
                <span class="text-brand-400 mt-0.5">▸</span>
                <span><strong class="opacity-100">Reinforcement Learning</strong> — MDPs, Q-Learning, DQN, A2C (CODAERUS)</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-brand-400 mt-0.5">▸</span>
                <span><strong class="opacity-100">DevOps Multicloud</strong> — Docker, K8s, Jenkins, Terraform (TecyLab)</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { inject } from 'vue'

const theme = inject('theme')

const phases = [
  {
    timeline: 'Now — 12 months',
    title: 'AI Backend Engineer / Applied ML Engineer',
    description: 'RAG systems, LLM orchestration, containerized AI apps, CI/CD for ML.',
    active: true,
  },
  {
    timeline: '1 — 3 years',
    title: 'AI Software Engineer / MLOps Engineer',
    description: 'Fine-tuning, autonomous agents, Continuous Training, RL in production.',
    active: false,
  },
  {
    timeline: '3 — 5+ years',
    title: 'Principal AI Architect / AI Tech Lead',
    description: 'Multi-model architectures, AI governance, technical leadership.',
    active: false,
  },
]
</script>
