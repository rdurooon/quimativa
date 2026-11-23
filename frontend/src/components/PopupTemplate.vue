<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { X } from '@lucide/vue';

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  searchPlaceholder: { type: String, default: '' },
  showClose: { type: Boolean, default: true },
  size: { type: String, default: 'large' },
});

const emit = defineEmits(['close']);
const panel = ref(null);
const closing = ref(false);
let closeTimer;

function close() {
  if (closing.value) return;
  closing.value = true;
  closeTimer = window.setTimeout(() => {
    closing.value = false;
    emit('close');
  }, window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 0 : 220);
}

function handleKeydown(event) {
  if (event.key === 'Escape') close();
}

async function focusPanel() {
  await nextTick();
  const target = props.showClose
    ? panel.value?.querySelector('[data-modal-close]')
    : panel.value?.querySelector('button');
  target?.focus();
}

watch(() => props.open, (open) => {
  if (!open) {
    closing.value = false;
    window.clearTimeout(closeTimer);
  }
  if (open) {
    document.body.style.overflow = 'hidden';
    focusPanel();
  } else {
    document.body.style.overflow = '';
  }
});

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  if (props.open) {
    document.body.style.overflow = 'hidden';
    focusPanel();
  }
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  document.body.style.overflow = '';
  window.clearTimeout(closeTimer);
});
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="popup-fundo"
      :class="{ 'popup-fundo-saindo': closing }"
      role="presentation"
      @mousedown.self="close"
    >
      <section
        ref="panel"
        class="popup-painel"
        :class="[
          `popup-painel-${size}`,
          {
            'popup-painel-sem-fechar': !showClose,
            'popup-painel-saindo': closing,
          },
        ]"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
      >
        <header v-if="searchPlaceholder" class="popup-cabecalho">
          <label class="popup-busca">
            <span class="sr-only">{{ searchPlaceholder }}</span>
            <input type="search" :placeholder="searchPlaceholder" />
          </label>
          <button
            v-if="showClose"
            class="popup-fechar"
            type="button"
            aria-label="Fechar"
            data-modal-close
            @click="close"
          >
            <X aria-hidden="true" />
          </button>
        </header>

        <button
          v-else-if="showClose"
          class="popup-fechar popup-fechar-sem-busca"
          type="button"
          aria-label="Fechar"
          data-modal-close
          @click="close"
        >
          <X aria-hidden="true" />
        </button>

        <div class="popup-conteudo">
          <h1 v-if="title">{{ title }}</h1>
          <p v-if="description">{{ description }}</p>
          <slot />
        </div>
      </section>
    </div>
  </Teleport>
</template>
