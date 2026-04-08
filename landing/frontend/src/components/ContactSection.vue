<template>
  <section id="contact" class="py-24 sm:py-32">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="section-animate text-center">
        <span class="inline-block text-xs font-semibold tracking-[0.2em] uppercase mb-4 opacity-50">Get in Touch</span>
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
          Let's <span class="gradient-text">Connect</span>
        </h2>
        <p class="text-base sm:text-lg max-w-xl mx-auto opacity-60 mb-12">
          Interested in working together or just want to chat about AI engineering? 
          I'm always open to new opportunities and conversations.
        </p>

        <!-- Contact cards -->
        <div class="grid sm:grid-cols-3 gap-4 max-w-2xl mx-auto stagger-children">
          <a v-for="link in contactLinks" :key="link.id"
             :href="link.href" target="_blank" rel="noopener noreferrer"
             class="glass-card rounded-xl p-6 text-center group"
             :id="'contact-' + link.id">
            <div class="w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center text-xl transition-transform group-hover:scale-110"
                 :style="{ background: `linear-gradient(135deg, ${link.colorFrom}20, ${link.colorTo}20)` }">
              <span v-html="link.icon"></span>
            </div>
            <h3 class="text-sm font-bold mb-1">{{ link.label }}</h3>
            <p class="text-xs opacity-50">{{ link.sublabel }}</p>
          </a>
        </div>

        <!-- Email direct -->
        <div class="mt-12 section-animate">
          <a href="mailto:hello@fernando.dev"
             class="inline-flex items-center gap-2 text-sm font-medium opacity-50 hover:opacity-100 transition-opacity"
             id="contact-email-direct">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            hello@fernando.dev
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const contactLinks = [
  {
    id: 'github',
    label: 'GitHub',
    sublabel: '@triplerush',
    href: 'https://github.com/triplerush',
    colorFrom: '#8b5cf6',
    colorTo: '#a855f7',
    icon: '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>',
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    sublabel: 'Fernando',
    href: 'https://linkedin.com/in/',
    colorFrom: '#3b82f6',
    colorTo: '#6366f1',
    icon: '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
  },
  {
    id: 'email',
    label: 'Email',
    sublabel: 'hello@fernando.dev',
    href: 'mailto:hello@fernando.dev',
    colorFrom: '#10b981',
    colorTo: '#06b6d4',
    icon: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>',
  },
]
</script>
