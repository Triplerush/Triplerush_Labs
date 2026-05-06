<template>
  <form class="constellation-search" role="search" @submit.prevent="submit">
    <label class="sr-only" for="constellation-query">Buscar en la constelación semántica</label>
    <div class="constellation-search__bar">
      <input
        id="constellation-query"
        ref="inputRef"
        :value="modelValue"
        type="search"
        maxlength="500"
        autocomplete="off"
        placeholder="Pregunta por RAG, FastAPI, MLOps, experiencia..."
        class="constellation-search__input"
        @input="$emit('update:modelValue', $event.target.value)"
        @keydown.escape="$emit('clear')"
      >
      <button class="constellation-search__submit" type="submit" :disabled="isSearching || !modelValue.trim()">
        <span v-if="isSearching">Buscando</span>
        <span v-else>Buscar</span>
      </button>
    </div>

    <div class="constellation-search__chips" aria-label="Sugerencias de búsqueda">
      <button
        v-for="suggestion in suggestions"
        :key="suggestion"
        type="button"
        class="constellation-search__chip"
        @click="pickSuggestion(suggestion)"
      >
        {{ suggestion }}
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

const suggestions = [
  'Sistemas RAG sobre PDFs',
  'Deploy de LLMs en producción',
  'FastAPI y microservicios',
  'Pipelines MLOps con Docker',
  'Arquitectura backend escalable',
]

const submit = () => emit('submit')

const pickSuggestion = (suggestion) => {
  emit('update:modelValue', suggestion)
  emit('submit', suggestion)
}

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style scoped>
.constellation-search {
  display: grid;
  gap: 14px;
  width: min(760px, calc(100vw - 32px));
}

.constellation-search__bar {
  display: flex;
  gap: 10px;
  padding: 8px;
  border: 1px solid oklch(1 0 0 / 0.10);
  border-radius: 18px;
  background: oklch(0.13 0.02 250 / 0.76);
  box-shadow: 0 20px 70px oklch(0 0 0 / 0.32);
  backdrop-filter: blur(18px);
}

.constellation-search__input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  color: oklch(0.94 0.01 250);
  font-size: 15px;
  line-height: 1.4;
  padding: 12px 12px 12px 16px;
}

.constellation-search__input::placeholder {
  color: oklch(0.80 0.02 250 / 0.48);
}

.constellation-search__input:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 6px;
  border-radius: 12px;
}

.constellation-search__submit {
  min-width: 112px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-accent-500));
  color: white;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}

.constellation-search__submit:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.constellation-search__submit:focus-visible,
.constellation-search__chip:focus-visible {
  outline: 2px solid var(--color-brand-400);
  outline-offset: 2px;
}

.constellation-search__chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.constellation-search__chip {
  min-height: 34px;
  padding: 6px 14px;
  border: 1px solid oklch(0.55 0.20 250 / 0.3);
  border-radius: 999px;
  background: transparent;
  color: oklch(0.90 0.01 250);
  font-size: 12px;
  cursor: pointer;
  transition: background-color 160ms ease, border-color 160ms ease;
}

.constellation-search__chip:hover {
  border-color: oklch(0.55 0.20 250 / 0.55);
  background: oklch(0.55 0.20 250 / 0.1);
}

@media (max-width: 640px) {
  .constellation-search__bar {
    flex-direction: column;
  }

  .constellation-search__submit {
    min-height: 44px;
  }

  .constellation-search__chip {
    min-height: 44px;
  }
}
</style>
