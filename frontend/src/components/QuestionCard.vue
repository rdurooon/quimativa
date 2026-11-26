<script setup>
import { computed } from "vue";
import { FileQuestionMark, Pencil, Trash2 } from "@lucide/vue";

const props = defineProps({
  questao: { type: Object, required: true },
  // Data URI da miniatura (vem da biblioteca de imagens); vazio quando não há imagem.
  imagem: { type: String, default: "" },
});

defineEmits(["editar", "remover"]);

const podeEditar = computed(() => props.questao.permissions?.edit === true);
const podeRemover = computed(() => props.questao.permissions?.delete === true);
</script>

<template>
  <article class="questao" :aria-label="`Questão: ${questao.statement}`">
    <div class="questao-miniatura">
      <img v-if="imagem" :src="imagem" alt="" />
      <FileQuestionMark v-else aria-hidden="true" />
    </div>

    <div class="questao-info">
      <h3 class="questao-enunciado">{{ questao.statement }}</h3>
      <p class="questao-detalhes">
        <span class="questao-minigame">{{ questao.minigame_name }}</span>
        <span>Pacote: {{ questao.package?.name ?? "Nenhum" }}</span>
        <span
          class="questao-dificuldade"
          :class="`questao-dificuldade-${questao.difficulty}`"
        >
          {{ questao.difficulty_name }}
        </span>
      </p>
    </div>

    <div class="questao-acoes">
      <button
        v-if="podeEditar"
        class="questao-editar"
        type="button"
        :aria-label="`Editar a questão ${questao.statement}`"
        @click="$emit('editar', questao)"
      >
        <Pencil aria-hidden="true" />
        Editar
      </button>
      <button
        v-if="podeRemover"
        class="questao-remover"
        type="button"
        :aria-label="`Remover a questão ${questao.statement}`"
        @click="$emit('remover', questao)"
      >
        <Trash2 aria-hidden="true" />
        Remover
      </button>
    </div>
  </article>
</template>

<style scoped>
.questao {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 12px 18px 12px 12px;
  border: 2px solid #c4ccc7;
  border-left: 8px solid var(--cor-azul-petroleo);
  border-radius: 16px;
  text-align: left;
}

.questao-miniatura {
  display: flex;
  height: 84px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 6px;
  border-radius: 10px;
  color: #9ba5a0;
  background: var(--cor-fundo);
}

/* Altura fixa no flex: o SVG encolhe para caber, seja qual for o tamanho original. */
.questao-miniatura img {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 0;
  object-fit: contain;
}
.questao-miniatura svg {
  width: 40px;
  height: 40px;
}

.questao-info {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.questao-enunciado {
  overflow: hidden;
  color: var(--cor-texto);
  font-size: 1.15rem;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.questao-detalhes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 14px;
  color: var(--cor-texto-secundario) !important;
  font-size: 0.95rem !important;
  font-weight: 700;
}

.questao-minigame {
  padding: 2px 10px;
  border-radius: 999px;
  color: var(--cor-texto-claro);
  background: var(--cor-azul-petroleo);
}

.questao-dificuldade {
  min-width: 80px;
  padding: 2px 12px;
  border-radius: 999px;
  color: #1e2a25;
  text-align: center;
}

.questao-dificuldade-1 {
  background: #5cb86a;
}
.questao-dificuldade-2 {
  background: #e0df55;
}
.questao-dificuldade-3 {
  background: #d9645e;
}

.questao-acoes {
  display: grid;
  gap: 8px;
}

.questao-editar,
.questao-remover {
  display: inline-flex;
  min-width: 140px;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 18px;
  border: 3px solid #d11a1a;
  border-radius: 999px;
  color: #d11a1a;
  background: var(--cor-superficie);
  font: 800 1rem var(--fonte);
  cursor: pointer;
}

.questao-editar {
  border-color: var(--cor-principal);
  color: var(--cor-principal);
}

.questao-remover:hover,
.questao-remover:focus-visible {
  background: rgba(209, 26, 26, 0.08);
}

.questao-editar:hover,
.questao-editar:focus-visible {
  background: rgba(0, 142, 21, 0.08);
}

.questao-editar svg,
.questao-remover svg {
  width: 22px;
  height: 22px;
}
</style>
