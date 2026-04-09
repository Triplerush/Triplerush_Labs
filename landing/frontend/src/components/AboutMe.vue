<template>
  <section id="about" class="py-24 sm:py-32">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="section-animate text-center mb-16">
        <span class="inline-block text-xs font-semibold tracking-[0.2em] uppercase mb-4 opacity-50">Sobre mi</span>
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
          Sobre <span class="gradient-text">Mi</span>
        </h2>
      </div>

      <!-- Bio — full width -->
      <div class="section-animate mb-8">
        <div class="glass-card rounded-2xl p-6 sm:p-8 hover:translate-y-0">
          <h3 class="text-xl font-bold mb-4">
            💻 Backend & AI Engineer
          </h3>
          <div class="space-y-4 text-sm sm:text-base opacity-75 leading-relaxed">
            <p>
              Soy Fernando - <strong class="opacity-100">Ingeniero de Sistemas</strong> especializado en 
              desarrollo backend y construcción de sistemas escalables, con experiencia en el diseño de 
              APIs robustas y arquitecturas mantenibles orientadas a producción.
            </p>
            <p>
              Trabajo principalmente con <strong class="opacity-100">Python (FastAPI)</strong> y 
              <strong class="opacity-100">Java (Spring Boot)</strong>, desarrollando servicios desacoplados, 
              seguros y eficientes. Tengo experiencia en modelado de datos, control de concurrencia, 
              integración de servicios y optimización de rendimiento en entornos distribuidos.
            </p>
            <p>
              He participado en la evolución de sistemas backend mediante refactorización de arquitecturas 
              monolíticas hacia enfoques modulares, así como en la construcción de microservicios con 
              buenas prácticas como separación por capas, manejo centralizado de errores y pruebas automatizadas.
            </p>
            <p>
              Complemento mi perfil con conocimientos en <strong class="opacity-100">machine learning aplicado</strong> 
              y procesamiento de datos, integrando capacidades de inteligencia artificial en soluciones backend 
              para construir sistemas más inteligentes, escalables y listos para producción.
            </p>
            <p>
              Manejo herramientas y tecnologías como <strong class="opacity-100">Docker, Redis, bases de datos relacionales 
              y pipelines de CI/CD</strong>, lo que me permite cubrir el ciclo completo de desarrollo, despliegue y operación.
            </p>
          </div>
        </div>
      </div>

      <!-- Certifications + Education — below bio -->
      <div class="grid lg:grid-cols-2 gap-8">
        <div class="section-animate" style="animation-delay: 0.2s;">
          <div class="glass-card rounded-2xl p-6 sm:p-8 hover:translate-y-0 h-full">
            <h3 class="text-xl font-bold mb-6">
              🏅 Certificaciones y Formacion
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
        </div>

        <div class="section-animate" style="animation-delay: 0.3s;">
          <!-- Education -->
          <div class="glass-card rounded-2xl p-6 sm:p-8 hover:translate-y-0 h-full">
            <h4 class="text-xl font-bold mb-6">🎓 Educacion</h4>
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0"
                   :class="theme === 'dark' ? 'bg-white/5' : 'bg-black/5'">
                🏛️
              </div>
              <div>
                <h4 class="text-base font-bold">Ingeniería de Sistemas</h4>
                <p class="text-sm opacity-50">Universidad Nacional de San Agustín (UNSA)</p>
                <p class="text-xs opacity-30 mt-0.5">2025</p>
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
    detail: 'MDPs, Q-Learning, DQN, REINFORCE, A2C - base técnica para RLHF',
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
