<template>
  <form class="constellation-search" role="search" @submit.prevent="submit">
    <label class="sr-only" for="constellation-query">Buscar en la constelación semántica</label>
    <div class="constellation-search__bar">
      <span class="constellation-search__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24"><path d="M11 4a7 7 0 015.66 11.07l4.13 4.13a1 1 0 01-1.41 1.41l-4.13-4.13A7 7 0 1111 4z" /></svg>
      </span>
      <input
        id="constellation-query"
        ref="inputRef"
        :value="modelValue"
        type="search"
        maxlength="500"
        autocomplete="off"
        placeholder="Buscar capacidad, proyecto o experiencia"
        class="constellation-search__input"
        @input="$emit('update:modelValue', $event.target.value)"
        @keydown.escape="$emit('clear')"
      >
      <button class="constellation-search__submit" type="submit" :disabled="isSearching || !modelValue.trim()">
        <span v-if="isSearching" class="constellation-search__loading">
          <span class="constellation-search__spinner" aria-hidden="true"></span>
          Buscando
        </span>
        <span v-else>Buscar</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { onMounted, ref } from 'vue'

defineProps({
  modelValue: { type: String, default: '' },
  isSearching: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit', 'clear'])
const inputRef = ref(null)

const submit = () => emit('submit')

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style scoped>
.constellation-search {
  display: grid;
  width: min(640px, calc(100vw - 32px));
}

.constellation-search__bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 6px 8px 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  backdrop-filter: blur(14px);
  transition: border-color 200ms var(--constellation-ease-out);
}

.constellation-search__bar:focus-within {
  border-color: var(--color-border-strong);
}

.constellation-search__icon {
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  color: var(--color-muted);
}

.constellation-search__icon svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
}

.constellation-search__input {
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--color-text);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.4;
  padding: 11px 4px;
}

.constellation-search__input::placeholder {
  color: var(--color-muted-2);
}

.constellation-search__submit {
  min-width: 96px;
  height: 36px;
  padding: 0 16px;
  border: 1px solid var(--color-accent);
  border-radius: 3px;
  background: transparent;
  color: var(--color-accent);
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 200ms ease;
}

.constellation-search__submit:hover:not(:disabled) {
  background: rgba(0, 229, 255, 0.10);
}

.constellation-search__loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.constellation-search__spinner {
  width: 11px;
  height: 11px;
  border: 1.5px solid rgba(0, 229, 255, 0.32);
  border-top-color: var(--color-accent);
  border-radius: 999px;
  animation: constellation-search-spin 780ms linear infinite;
}

.constellation-search__submit:disabled {
  cursor: not-allowed;
  opacity: 0.4;
  border-color: var(--color-border);
  color: var(--color-muted);
}

.constellation-search__submit:focus-visible {
  outline: 1px solid var(--color-accent);
  outline-offset: 2px;
}

@keyframes constellation-search-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .constellation-search__bar {
    grid-template-columns: auto 1fr;
    padding: 8px;
  }

  .constellation-search__submit {
    grid-column: 1 / -1;
    min-height: 40px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-search__spinner {
    animation: none;
  }
}
</style>
