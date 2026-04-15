<template>
  <div v-if="isDesktop"
       ref="cursor"
       class="fixed top-0 left-0 w-5 h-5 rounded-full pointer-events-none z-[10000] mix-blend-difference bg-white"
       :style="{ transform: `translate(${x}px, ${y}px) scale(${scale})`, transition: 'transform 0.15s ease-out' }">
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const x = ref(-40)
const y = ref(-40)
const scale = ref(1)
const isDesktop = ref(false)

function onMouseMove(e) {
  x.value = e.clientX - 10
  y.value = e.clientY - 10
}

function onEnterInteractive() { scale.value = 2.5 }
function onLeaveInteractive() { scale.value = 1 }

function bindInteractives() {
  document.querySelectorAll('a, button, .glass-card').forEach(el => {
    el.addEventListener('mouseenter', onEnterInteractive)
    el.addEventListener('mouseleave', onLeaveInteractive)
  })
}

let mutationObserver = null

onMounted(() => {
  isDesktop.value = window.matchMedia('(hover: hover)').matches
  if (!isDesktop.value) return

  document.addEventListener('mousemove', onMouseMove)
  bindInteractives()

  // Re-bind when DOM changes (e.g. projects loaded, chat opened)
  mutationObserver = new MutationObserver(() => bindInteractives())
  mutationObserver.observe(document.body, { childList: true, subtree: true })
})

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onMouseMove)
  if (mutationObserver) mutationObserver.disconnect()
})
</script>

<style>
@media (hover: hover) {
  body { cursor: none !important; }
  a, button, .glass-card { cursor: none !important; }
}
</style>
