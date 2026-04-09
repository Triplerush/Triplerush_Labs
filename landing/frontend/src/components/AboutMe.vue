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
                discipline to the world of ML. Currently at <strong class="opacity-100">PHAXSI</strong>, 
                I've refactored a monolithic backend (~3,200 LOC) into a modular architecture and 
                achieved a <strong class="opacity-100">10× performance improvement</strong> on geospatial 
                reporting pipelines.
              </p>
              <p>
                Previously at <strong class="opacity-100">Anyone AI</strong>, I led the development of a 
                <strong class="opacity-100">RAG system</strong> for insurance policy queries using OpenSearch 
                and LangChain, and built ML pipelines that improved model accuracy by up to 15%.
              </p>
              <p>
                My unique value? I bridge the gap between the AI researcher who creates a model 
                and the infrastructure needed to scale it. From <strong class="opacity-100">semantic search 
                with FAISS/OpenSearch</strong> to <strong class="opacity-100">Docker/Kubernetes deployments</strong>,
                I own the full lifecycle.
              </p>
            </div>
          </div>
        </div>

        <!-- Certifications column -->
        <div class="lg:col-span-2 section-animate" style="animation-delay: 0.2s;">
          <div class="glass-card rounded-2xl p-6 sm:p-8 hover:translate-y-0">
            <h3 class="text-xl font-bold mb-6">
              🏅 Certifications & Training
            </h3>

            <div class="space-y-4">
              <div v-for="cert in certifications" :key="cert.name"
                   class="group relative pl-4 border-l-2 transition-all duration-200"
                   :class="theme === 'dark' 
                     ? 'border-white/10 hover:border-brand-400' 
                     : 'border-black/10 hover:border-brand-500'">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <h4 class="text-sm font-bold leading-tight">{{ cert.name }}</h4>
                    <p class="text-xs mt-0.5"
                       :class="theme === 'dark' ? 'text-brand-300' : 'text-brand-600'">
                      {{ cert.institution }}
                    </p>
                  </div>
                  <span class="text-[10px] font-semibold tracking-wider uppercase shrink-0 px-2 py-0.5 rounded-full"
                        :class="theme === 'dark' 
                          ? 'bg-white/5 text-white/50' 
                          : 'bg-black/5 text-black/40'">
                    {{ cert.year }}
                  </span>
                </div>
                <p v-if="cert.detail" class="text-xs mt-1 opacity-40">{{ cert.detail }}</p>
              </div>
            </div>
          </div>

          <!-- Education -->
          <div class="glass-card rounded-2xl p-6 mt-6 hover:translate-y-0">
            <h4 class="text-sm font-bold mb-3 opacity-70">🎓 Education</h4>
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm shrink-0"
                   :class="theme === 'dark' ? 'bg-white/5' : 'bg-black/5'">
                🏛️
              </div>
              <div>
                <h4 class="text-sm font-bold">Ingeniería de Sistemas</h4>
                <p class="text-xs opacity-50">Universidad Nacional de San Agustín (UNSA)</p>
                <p class="text-[10px] opacity-30 mt-0.5">2025</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { inject } from 'vue'

const theme = inject('theme')

const certifications = [
  {
    name: 'Soluciones de IA con Agentes Autónomos',
    institution: 'AnyoneAI',
    year: '2025',
    detail: 'Desarrollo de soluciones de inteligencia artificial basadas en agentes',
  },
  {
    name: 'Aplicaciones basadas en LLMs',
    institution: 'AnyoneAI',
    year: '2025',
    detail: 'Construcción de aplicaciones sobre modelos de lenguaje',
  },
  {
    name: 'Especialista en DevOps Multicloud',
    institution: 'TecyLab',
    year: '2025',
    detail: 'Docker, K8s (EKS/AKS), Jenkins, GitHub Actions, Azure DevOps, SonarQube, Terraform',
  },
  {
    name: 'Aprendizaje por Refuerzo con Python',
    institution: 'CODAERUS',
    year: '2025',
    detail: 'MDPs, Q-Learning, DQN, REINFORCE, A2C — base técnica para RLHF',
  },
  {
    name: 'Programación Senior con Spring Boot',
    institution: 'TecyLab',
    year: '2024',
    detail: 'Multicloud y Microservicios',
  },
  {
    name: 'Oracle Next Education F2 T4 Back-end',
    institution: 'Alura Latam',
    year: '2023',
    detail: null,
  },
]
</script>
