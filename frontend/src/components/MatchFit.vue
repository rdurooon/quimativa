<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';

const area = ref(null);
const conteudo = ref(null);
const escala = ref(1);
let observador;

function encaixar() {
  const altura = area.value.clientHeight;
  const largura = area.value.clientWidth;
  const alturaConteudo = conteudo.value.offsetHeight;
  const larguraConteudo = conteudo.value.scrollWidth;
  if (!altura || !largura || !alturaConteudo || !larguraConteudo) return;
  escala.value = Math.min(1, altura / alturaConteudo, largura / larguraConteudo);
}

onMounted(() => {
  encaixar();
  if (typeof ResizeObserver === 'undefined') return;
  observador = new ResizeObserver(encaixar);
  observador.observe(area.value);
  observador.observe(conteudo.value);
});
onBeforeUnmount(() => observador?.disconnect());
</script>

<template>
  <div ref="area" class="encaixe-partida">
    <div ref="conteudo" class="encaixe-conteudo" :style="{ '--encaixe-escala': escala }">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.encaixe-partida { position: relative; min-width: 0; min-height: 0; }
.encaixe-conteudo {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  transform: translate(-50%, -50%) scale(var(--encaixe-escala));
}
.encaixe-superior .encaixe-conteudo {
  top: 0;
  transform-origin: center top;
  transform: translateX(-50%) scale(var(--encaixe-escala));
}
</style>
