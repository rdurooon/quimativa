<script setup>
import { onBeforeUnmount, onMounted, ref, useSlots, watch } from 'vue';

const props = defineProps({
  alunos: { type: Array, required: true },
  equipe: { type: String, required: true },
});
const editavel = Boolean(useSlots().default);
const area = ref(null);
const lista = ref(null);
const faixa = ref(null);
const modo = ref('');
let observador;

function ajustarLista() {
  const altura = area.value.clientHeight;
  const largura = area.value.clientWidth;
  if (!altura || !largura) return;

  const cabe = () => lista.value.offsetHeight <= altura && lista.value.scrollWidth <= largura;
  opcoes: for (const densidade of ['normal', 'compacta', 'reduzida']) {
    lista.value.dataset.densidade = densidade;
    for (let colunas = 1; colunas <= Math.min(3, Math.max(1, props.alunos.length)); colunas++) {
      lista.value.style.setProperty('--colunas', colunas);
      if (cabe()) break opcoes;
    }
  }

  const excede = !cabe();
  modo.value = excede ? (editavel ? 'rolagem' : 'faixa') : '';
  faixa.value?.style.setProperty('--largura-lista', `${largura}px`);
  if (faixa.value) {
    const distancia = faixa.value.firstElementChild.offsetWidth;
    faixa.value.style.setProperty('--duracao-faixa', `${distancia / 42}s`);
  }
}

watch(() => props.alunos.map(({ nome }) => nome), ajustarLista, { flush: 'post' });
onMounted(() => {
  ajustarLista();
  if (typeof ResizeObserver === 'undefined') return;
  observador = new ResizeObserver(ajustarLista);
  observador.observe(area.value);
  observador.observe(lista.value);
  if (faixa.value) observador.observe(faixa.value);
});
onBeforeUnmount(() => observador?.disconnect());
</script>

<template>
  <div
    ref="area"
    class="lista-equipe"
    :class="modo"
    :tabindex="modo ? 0 : undefined"
  >
    <ul ref="lista" class="lista-equipe-grade" :aria-label="`Alunos da equipe ${equipe}`">
      <li v-for="(aluno, indice) in alunos" :key="aluno.id">
        <span class="lista-equipe-nome">{{ aluno.nome }}</span>
        <slot :aluno="aluno" :posicao="indice" />
      </li>
    </ul>
    <div v-if="!editavel" ref="faixa" class="lista-equipe-faixa" aria-hidden="true">
      <div v-for="copia in 2" :key="copia" class="lista-equipe-faixa-grupo">
        <span v-for="aluno in alunos" :key="aluno.id">{{ aluno.nome }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lista-equipe {
  position: relative;
  width: 100%;
  min-width: 0;
  min-height: 0;
  flex: 1 1 0;
  overflow: hidden;
  line-height: 1.3;
}
.lista-equipe-grade {
  display: grid;
  grid-template-columns: repeat(var(--colunas, 1), minmax(0, 1fr));
  gap: .2em .65em;
  list-style: none;
  margin: 0;
  padding: 0;
  text-align: left;
}
.lista-equipe-grade[data-densidade="compacta"] {
  gap: .12em .5em;
  font-size: max(.8rem, .9em);
  line-height: 1.2;
}
.lista-equipe-grade[data-densidade="reduzida"] {
  gap: .06em .4em;
  font-size: max(.75rem, .8em);
  line-height: 1.15;
}
.lista-equipe-grade li { display: flex; align-items: center; justify-content: space-between; gap: 4px; }
.lista-equipe-nome { min-width: 0; overflow-wrap: anywhere; }
.rolagem { overflow: auto; }
.lista-equipe-faixa {
  display: flex;
  position: absolute;
  top: 50%;
  left: 0;
  width: max-content;
  visibility: hidden;
}
.lista-equipe-faixa-grupo {
  display: flex;
  justify-content: space-between;
  gap: 2em;
  min-width: var(--largura-lista, 0px);
  padding-right: 2em;
  white-space: nowrap;
}
.faixa .lista-equipe-grade { position: absolute; inset: 0 0 auto; clip-path: inset(50%); }
.faixa .lista-equipe-faixa {
  visibility: visible;
  animation: desfilar var(--duracao-faixa) linear infinite;
}
.faixa:hover .lista-equipe-faixa,
.faixa:focus-within .lista-equipe-faixa { animation-play-state: paused; }
@keyframes desfilar {
  from { transform: translate(0, -50%); }
  to { transform: translate(-50%, -50%); }
}
@media (prefers-reduced-motion: reduce) {
  .faixa { overflow: auto; }
  .faixa .lista-equipe-grade { position: static; clip-path: none; }
  .faixa .lista-equipe-faixa { visibility: hidden; animation: none; }
}
</style>
