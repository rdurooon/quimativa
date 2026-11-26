<script setup>
import { onBeforeUnmount, ref, watch } from 'vue';

const props = defineProps({
  valor: { type: Number, required: true },
});
const exibido = ref(props.valor);
let quadro;

watch(() => props.valor, (destino, anterior) => {
  window.cancelAnimationFrame(quadro);
  if (destino <= anterior || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    exibido.value = destino;
    return;
  }

  const origem = exibido.value;
  const inicio = performance.now();
  function atualizar() {
    const progresso = Math.min(1, (performance.now() - inicio) / 650);
    exibido.value = Math.round(origem + (destino - origem) * (1 - (1 - progresso) ** 3));
    if (progresso < 1) quadro = window.requestAnimationFrame(atualizar);
  }
  quadro = window.requestAnimationFrame(atualizar);
});

onBeforeUnmount(() => window.cancelAnimationFrame(quadro));
</script>

<template>
  <span class="contador-placar">
    <span :key="valor" class="contador-valor" :class="{ 'contador-deslizando': exibido !== valor }" aria-hidden="true">{{ exibido }}</span>
    <span class="sr-only">{{ valor }}</span>
  </span>
</template>

<style scoped>
.contador-placar { display: inline-block; overflow: clip; font-variant-numeric: tabular-nums; vertical-align: bottom; }
.contador-valor { display: inline-block; }
.contador-deslizando { animation: subir-contador 300ms ease-out both; }
@keyframes subir-contador {
  from { opacity: .45; transform: translateY(.75em); }
  to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  .contador-deslizando { animation: none; }
}
</style>
