<script setup>
import GradeCartas from "./GradeCartas.vue";

const rascunho = defineModel("rascunho", { required: true });

defineProps({
  erros: { type: Object, default: () => ({}) },
});

// Uma única carta correta: marcar outra troca a escolha; clicar de novo desmarca.
function alternar(id) {
  rascunho.value.correta = rascunho.value.correta === id ? null : id;
}

const marcado = (id) => rascunho.value.correta === id;
const rotulo = (id, indice) => `Carta ${indice + 1} é a correta`;
</script>

<template>
  <div class="form-cartas">
    <label class="sr-only" for="molecula-enunciado">Enunciado</label>
    <input
      id="molecula-enunciado"
      v-model="rascunho.enunciado"
      class="form-enunciado"
      :class="{ 'form-campo-invalido': erros.statement }"
      type="text"
      maxlength="2000"
      placeholder="Adicionar texto do enunciado..."
    />
    <p v-if="erros.statement" class="form-erro" role="alert">
      {{ erros.statement }}
    </p>

    <GradeCartas
      v-model:cartas="rascunho.cartas"
      :erros="erros"
      :marcado="marcado"
      :rotulo-marcador="rotulo"
      @alternar="alternar"
    />
    <p class="form-dica">
      Escreva a função orgânica no enunciado e marque a carta correta.
    </p>
    <p v-if="erros['payload.correct_card_id']" class="form-erro" role="alert">
      {{ erros["payload.correct_card_id"] }}
    </p>
  </div>
</template>

<style scoped>
.form-cartas {
  display: grid;
  gap: 12px;
}

.form-enunciado {
  width: min(100%, 640px);
  height: 48px;
  justify-self: center;
  padding: 0 16px;
  border: 3px solid #9ba5a0;
  border-radius: 22px;
  color: var(--cor-texto);
  background: var(--cor-superficie);
  font: 700 1.2rem var(--fonte);
}

.form-enunciado:focus-visible {
  outline: none;
  border-color: var(--cor-principal);
}

.form-campo-invalido {
  border-color: #d11a1a;
}

.form-dica {
  font-size: 0.95rem !important;
  text-align: center;
}

.form-erro {
  color: #d11a1a !important;
  font-size: 0.95rem !important;
  font-weight: 700;
  text-align: center;
}
</style>
