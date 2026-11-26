<script setup>
import { Check } from "@lucide/vue";

// Círculo do canto da caixa: mostra o check ou, na Ordem das funções, o número da posição.
defineProps({
  marcado: { type: Boolean, default: false },
  numero: { type: Number, default: null },
  rotulo: { type: String, required: true },
  desabilitado: { type: Boolean, default: false },
});

defineEmits(["alternar"]);
</script>

<template>
  <button
    class="marcador"
    :class="{ 'marcador-ativo': marcado }"
    type="button"
    :aria-pressed="marcado ? 'true' : 'false'"
    :aria-label="rotulo"
    :title="rotulo"
    :disabled="desabilitado"
    @click="$emit('alternar')"
  >
    <span v-if="numero !== null" class="marcador-numero">{{ numero }}</span>
    <Check v-else aria-hidden="true" />
  </button>
</template>

<style scoped>
.marcador {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border: 2px solid #9ba5a0;
  border-radius: 50%;
  color: #9ba5a0;
  background: var(--cor-superficie);
  cursor: pointer;
}

.marcador svg {
  width: 26px;
  height: 26px;
}

.marcador:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 142, 21, 0.3);
}

.marcador-ativo {
  border-color: var(--cor-principal);
  color: var(--cor-texto-claro);
  background: var(--cor-principal);
}

.marcador-numero {
  font: 800 1.3rem var(--fonte);
}

.marcador:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
