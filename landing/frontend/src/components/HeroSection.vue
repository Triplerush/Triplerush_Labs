<template>
  <section id="hero" class="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-1/4 -left-32 w-96 h-96 rounded-full opacity-20 blur-3xl animate-float"
           style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));">
      </div>
      <div class="absolute bottom-1/4 -right-32 w-80 h-80 rounded-full opacity-15 blur-3xl animate-float"
           style="background: linear-gradient(135deg, var(--color-accent-500), var(--color-brand-400)); animation-delay: 3s;">
      </div>
      <!-- Grid pattern -->
      <div class="absolute inset-0 opacity-[0.03]"
           style="background-image: radial-gradient(circle, currentColor 1px, transparent 1px); background-size: 40px 40px;">
      </div>
    </div>

    <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <!-- Badge -->
      <div class="animate-fade-in-down inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium tracking-wide mb-8 border"
           :class="theme === 'dark' 
             ? 'bg-brand-500/10 text-brand-300 border-brand-500/20' 
             : 'bg-brand-500/10 text-brand-700 border-brand-500/20'">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
        </span>
        Open to opportunities
      </div>

      <!-- Name -->
      <h1 class="animate-fade-in-up text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight mb-4">
        <span class="gradient-text">Fernando</span>
      </h1>

      <!-- Title -->
      <p class="animate-fade-in-up text-xl sm:text-2xl md:text-3xl font-semibold mb-4 opacity-90"
         style="animation-delay: 0.15s;">
        AI Software Engineer
      </p>

      <!-- Tagline -->
      <p class="animate-fade-in-up text-base sm:text-lg md:text-xl font-light max-w-2xl mx-auto mb-10 opacity-60"
         style="animation-delay: 0.3s;">
        Building AI that ships to production — bridging ML, DevOps, and AI Engineering
        to create intelligent systems that scale.
      </p>

      <!-- CTA Buttons -->
      <div class="animate-fade-in-up flex flex-wrap items-center justify-center gap-4"
           style="animation-delay: 0.45s;">
        <a href="https://github.com/triplerush" target="_blank" rel="noopener noreferrer"
           class="group inline-flex items-center gap-2.5 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 text-white"
           style="background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));"
           id="hero-github">
          <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          GitHub
        </a>

        <a href="https://linkedin.com/in/" target="_blank" rel="noopener noreferrer"
           class="group inline-flex items-center gap-2.5 px-6 py-3 rounded-xl font-semibold text-sm border transition-all duration-300 hover:scale-105"
           :class="theme === 'dark' 
             ? 'border-white/20 hover:border-brand-400 hover:bg-white/5' 
             : 'border-black/20 hover:border-brand-500 hover:bg-black/5'"
           id="hero-linkedin">
          <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
          </svg>
          LinkedIn
        </a>

        <a href="#contact"
           class="group inline-flex items-center gap-2.5 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 opacity-70 hover:opacity-100"
           id="hero-cv">
          <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download CV
        </a>
      </div>

      <!-- Scroll indicator -->
      <div class="animate-fade-in absolute bottom-8 left-1/2 -translate-x-1/2 opacity-40"
           style="animation-delay: 1s;">
        <div class="flex flex-col items-center gap-2">
          <span class="text-xs tracking-widest uppercase">Scroll</span>
          <div class="w-5 h-8 rounded-full border-2 border-current flex items-start justify-center p-1">
            <div class="w-1 h-2 rounded-full bg-current animate-bounce"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { inject } from 'vue'
const theme = inject('theme')
</script>
