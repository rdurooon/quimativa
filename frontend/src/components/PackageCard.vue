<script setup>
import { computed } from "vue";
import { Check, Trash2 } from "@lucide/vue";

const props = defineProps({
  pacote: { type: Object, required: true },
  minigames: { type: Array, default: () => [] },
  difficulties: { type: Array, default: () => [] },
});

defineEmits(["remover"]);

// Troca os valores do pacote (ex.: 'identification', 1) pelos nomes vindos de questoes_metadados().
function comNomes(valores, catalogo) {
  const nomes = new Map(catalogo.map((item) => [item.value, item.name]));
  return valores.map((valor) => ({
    value: valor,
    name: nomes.get(valor) ?? String(valor),
  }));
}

const minigamesPresentes = computed(() =>
  comNomes(props.pacote.minigame_types ?? [], props.minigames),
);
const dificuldadesPresentes = computed(() =>
  comNomes(props.pacote.difficulties ?? [], props.difficulties),
);
const jaInstalado = computed(() => props.pacote.kind === "base");
const podeRemover = computed(() => props.pacote.permissions?.delete === true);
</script>

<template>
  <article class="pacote" :aria-label="`Pacote ${pacote.name}`">
    <h2 class="pacote-nome">{{ pacote.name }}</h2>

    <div v-if="minigamesPresentes.length" class="pacote-minigames">
      <p class="pacote-rotulo">Contém questões para os seguintes minigames:</p>
      <ul>
        <li v-for="minigame in minigamesPresentes" :key="minigame.value">
          {{ minigame.name }}
        </li>
      </ul>
    </div>
    <p v-else class="pacote-vazio">Este pacote ainda não tem questões.</p>

    <div v-if="dificuldadesPresentes.length" class="pacote-dificuldades">
      <p class="pacote-rotulo">Dificuldades presentes:</p>
      <ul>
        <li
          v-for="dificuldade in dificuldadesPresentes"
          :key="dificuldade.value"
        >
          <span
            class="chip-dificuldade"
            :class="`chip-dificuldade-${dificuldade.value}`"
          >
            {{ dificuldade.name }}
          </span>
        </li>
      </ul>
    </div>

    <div class="pacote-acoes">
      <span v-if="jaInstalado" class="pacote-instalado">
        <Check aria-hidden="true" />
        Já instalado
      </span>
      <button
        v-if="podeRemover"
        class="pacote-remover"
        type="button"
        @click="$emit('remover', pacote)"
      >
        <Trash2 aria-hidden="true" />
        Remover
      </button>
    </div>
  </article>
</template>

<style scoped>
.pacote {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) auto;
  grid-template-areas:
    "nome nome nome"
    "minigames dificuldades acoes";
  gap: 10px 24px;
  padding: 20px 24px;
  border: 3px solid #9ba5a0;
  border-radius: 22px;
  text-align: left;
}

.pacote-nome {
  grid-area: nome;
  color: var(--cor-principal);
  font-size: 1.5rem;
}

.pacote-minigames {
  grid-area: minigames;
}
.pacote-dificuldades {
  grid-area: dificuldades;
}
.pacote-vazio {
  grid-column: 1 / 3;
}

.pacote-rotulo,
.pacote-vazio {
  color: var(--cor-texto-secundario);
  font-weight: 700;
}

ul {
  display: grid;
  margin: 8px 0 0;
  padding: 0;
  gap: 4px;
  list-style: none;
  color: var(--cor-texto-secundario);
  font-size: 0.95rem;
  font-weight: 600;
}

.pacote-minigames li::before {
  content: "- ";
}

.pacote-dificuldades ul {
  justify-items: start;
  gap: 10px;
}

.chip-dificuldade {
  display: inline-block;
  min-width: 112px;
  padding: 4px 18px;
  border-radius: 999px;
  color: #1e2a25;
  font-weight: 800;
  text-align: center;
}

.chip-dificuldade-1 {
  background: #5cb86a;
}
.chip-dificuldade-2 {
  background: #e0df55;
}
.chip-dificuldade-3 {
  background: #d9645e;
}

.pacote-acoes {
  grid-area: acoes;
  display: grid;
  align-content: center;
  gap: 14px;
}

.pacote-instalado,
.pacote-remover {
  display: inline-flex;
  min-width: 224px;
  min-height: 56px;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 3px solid;
  border-radius: 999px;
  font: 800 1.15rem var(--fonte);
}

.pacote-instalado {
  border-color: #9ba5a0;
  color: var(--cor-texto-secundario);
}

.pacote-remover {
  border-color: #d11a1a;
  color: #d11a1a;
  background: var(--cor-superficie);
  cursor: pointer;
}

.pacote-remover:hover,
.pacote-remover:focus-visible {
  background: rgba(209, 26, 26, 0.08);
}

.pacote-instalado svg,
.pacote-remover svg {
  width: 28px;
  height: 28px;
}
</style>
