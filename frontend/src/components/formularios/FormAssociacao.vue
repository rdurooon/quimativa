<script setup>
import GradeCartas from "./GradeCartas.vue";

const rascunho = defineModel("rascunho", { required: true });

defineProps({
  erros: { type: Object, default: () => ({}) },
});

// Par correto: no máximo duas cartas; para trocar, o professor desmarca uma primeiro.
function alternar(id) {
  const par = rascunho.value.par;
  if (par.includes(id)) rascunho.value.par = par.filter((item) => item !== id);
  else if (par.length < 2) rascunho.value.par = [...par, id];
}

const marcado = (id) => rascunho.value.par.includes(id);
const desabilitado = (id) => rascunho.value.par.length >= 2 && !marcado(id);
const rotulo = (id, indice) => `Carta ${indice + 1} faz parte do par correto`;
</script>

<template>
  <div class="form-cartas">
    <label class="sr-only" for="associacao-enunciado">Enunciado</label>
    <input
      id="associacao-enunciado"
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
      :desabilitado="desabilitado"
      :rotulo-marcador="rotulo"
      @alternar="alternar"
    />
    <p class="form-dica">Marque as duas cartas que formam o par correto.</p>
    <p v-if="erros['payload.correct_pair']" class="form-erro" role="alert">
      {{ erros["payload.correct_pair"] }}
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
