<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { X } from '@lucide/vue';
import { activateModal, deactivateModal, getModalIndex, getTopModal } from '../services/modalStack';

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
const isTopModal = computed(() => getTopModal() === panel);
const modalIndex = computed(() => getModalIndex(panel));
let closeTimer = null;
let previouslyFocused = null;
let listenerActive = false;

const focusableSelector = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',');

function isAvailable(element) {
  return element?.isConnected && !element.disabled
    && element.getAttribute('aria-hidden') !== 'true';
}

function activate() {
  if (listenerActive) return;
  previouslyFocused = document.activeElement;
  listenerActive = true;
  activateModal(panel);
  window.addEventListener('keydown', handleKeydown);
  focusPanel();
}

function deactivate() {
  if (!listenerActive) return;
  const wasTopModal = isTopModal.value;
  const focusTarget = previouslyFocused;
  listenerActive = false;
  deactivateModal(panel);
  window.removeEventListener('keydown', handleKeydown);
  if (wasTopModal) {
    const nextTopModal = getTopModal();
    if (!nextTopModal) {
      if (isAvailable(focusTarget)) focusTarget.focus();
    } else {
      nextTick(() => {
        if (getTopModal() !== nextTopModal) return;
        const nextPanel = nextTopModal.value;
        if (isAvailable(focusTarget) && nextPanel?.contains(focusTarget)) {
          focusTarget.focus();
        } else {
          const target = nextPanel?.querySelector('[data-modal-close]')
            ?? nextPanel?.querySelector('button')
            ?? nextPanel;
          target?.focus();
        }
      });
    }
  }
  previouslyFocused = null;
}

function close() {
  if (!props.open || closing.value) return;
  closing.value = true;
  closeTimer = window.setTimeout(() => {
    closeTimer = null;
    if (!props.open) return;
    closing.value = false;
    emit('close');
  }, window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 0 : 220);
}

function handleKeydown(event) {
  if (!props.open || !listenerActive || !isTopModal.value) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    close();
    return;
  }
  if (event.key !== 'Tab') return;

  const elements = [...(panel.value?.querySelectorAll(focusableSelector) ?? [])]
    .filter(isAvailable);
  if (!elements.length) {
    event.preventDefault();
    panel.value?.focus();
    return;
  }

  const first = elements[0];
  const last = elements[elements.length - 1];
  if (event.shiftKey && (document.activeElement === first || !panel.value?.contains(document.activeElement))) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && (document.activeElement === last || !panel.value?.contains(document.activeElement))) {
    event.preventDefault();
    first.focus();
  }
}

async function focusPanel() {
  await nextTick();
  const target = props.showClose
    ? panel.value?.querySelector('[data-modal-close]')
    : panel.value?.querySelector('button');
  (target ?? panel.value)?.focus();
}

watch(() => props.open, (open) => {
  if (open) {
    closing.value = false;
    activate();
    return;
  }
  closing.value = false;
  if (closeTimer !== null) {
    window.clearTimeout(closeTimer);
    closeTimer = null;
  }
  deactivate();
});

onMounted(() => {
  if (props.open) activate();
});

onUnmounted(() => {
  if (closeTimer !== null) window.clearTimeout(closeTimer);
  deactivate();
});
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="popup-fundo"
      :class="{ 'popup-fundo-saindo': closing }"
      :style="{ zIndex: 100 + modalIndex }"
      role="presentation"
      :aria-hidden="isTopModal ? 'false' : 'true'"
      :inert="!isTopModal"
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
        :aria-modal="isTopModal ? 'true' : undefined"
        :aria-label="title"
        tabindex="-1"
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
