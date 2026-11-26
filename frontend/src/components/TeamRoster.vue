<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { ChevronLeft, ChevronRight } from '@lucide/vue';

const props = defineProps({
  alunos: { type: Array, required: true },
  equipe: { type: String, required: true },
});
const area = ref(null);
const capacidade = ref(Infinity);
const pagina = ref(0);
const porPagina = computed(() => props.alunos.length > capacidade.value
  ? Math.max(1, capacidade.value - 1)
  : Math.max(1, props.alunos.length));
const total = computed(() => Math.max(1, Math.ceil(props.alunos.length / porPagina.value)));
const atual = computed(() => Math.min(pagina.value, total.value - 1));
const inicio = computed(() => atual.value * porPagina.value);
const visiveis = computed(() => props.alunos.slice(inicio.value, inicio.value + porPagina.value));
let observador;

watch(() => props.alunos.length, (quantidade, anterior) => {
  pagina.value = quantidade > anterior ? total.value - 1 : atual.value;
});

onMounted(() => {
  if (typeof ResizeObserver === 'undefined') return;
  observador = new ResizeObserver(() => {
    const linha = parseFloat(window.getComputedStyle(area.value).lineHeight);
    if (linha > 0) capacidade.value = Math.max(1, Math.floor(area.value.clientHeight / linha));
  });
  observador.observe(area.value);
});
onBeforeUnmount(() => observador?.disconnect());
</script>

<template>
  <div ref="area" class="lista-equipe">
    <ul :aria-label="`Alunos da equipe ${equipe}`">
      <li v-for="(aluno, indice) in visiveis" :key="aluno.id">
        <span class="lista-equipe-nome" :title="aluno.nome">{{ aluno.nome }}</span>
        <slot :aluno="aluno" :posicao="inicio + indice" />
      </li>
    </ul>
    <nav v-if="total > 1" class="lista-equipe-paginas" :aria-label="`Páginas de alunos da equipe ${equipe}`">
      <button type="button" :disabled="atual === 0" :aria-label="`Página anterior da equipe ${equipe}`" @click="pagina = atual - 1">
        <ChevronLeft aria-hidden="true" />
      </button>
      <span>{{ atual + 1 }} / {{ total }}</span>
      <button type="button" :disabled="atual === total - 1" :aria-label="`Próxima página da equipe ${equipe}`" @click="pagina = atual + 1">
        <ChevronRight aria-hidden="true" />
      </button>
    </nav>
  </div>
</template>

<style scoped>
.lista-equipe { width: 100%; min-height: 0; flex: 1 1 0; line-height: 1.65em; }
.lista-equipe ul { list-style: none; }
.lista-equipe li, .lista-equipe-paginas { display: flex; align-items: center; justify-content: space-between; gap: 4px; height: 1.65em; }
.lista-equipe-nome { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lista-equipe-paginas button {
  display: grid; place-items: center; background: var(--cor-superficie); color: var(--cor-principal-escura);
  border: 1px solid var(--cor-linha); border-radius: 5px; padding: 0 3px; cursor: pointer;
}
.lista-equipe-paginas button:disabled { opacity: .4; cursor: default; }
.lista-equipe-paginas svg { width: 1em; height: 1em; }
</style>
