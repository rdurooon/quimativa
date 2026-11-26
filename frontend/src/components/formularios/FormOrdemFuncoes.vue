<script setup>
import GradeCartas from "./GradeCartas.vue";

const rascunho = defineModel("rascunho", { required: true });

defineProps({
  erros: { type: Object, default: () => ({}) },
});

// Marcar põe a caixa no fim da sequência; desmarcar a tira e as seguintes sobem uma posição.
function alternar(id) {
  const ordem = rascunho.value.ordem;
  if (ordem.includes(id))
    rascunho.value.ordem = ordem.filter((item) => item !== id);
  else if (ordem.length < rascunho.value.cartas.length)
    rascunho.value.ordem = [...ordem, id];
}

const marcado = (id) => rascunho.value.ordem.includes(id);
const numero = (id) =>
  marcado(id) ? rascunho.value.ordem.indexOf(id) + 1 : null;
const rotulo = (id, indice) =>
  marcado(id)
    ? `Molécula ${indice + 1} na posição ${numero(id)}. Desmarcar`
    : `Colocar a molécula ${indice + 1} na próxima posição`;
</script>

<template>
  <div class="form-cartas">
    <label class="sr-only" for="ordem-enunciado">Enunciado</label>
    <input
      id="ordem-enunciado"
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
      somente-imagem
      prefixo-erro="payload.molecules"
      :marcado="marcado"
      :numero="numero"
      :rotulo-marcador="rotulo"
      @alternar="alternar"
    />
    <p class="form-dica">
      Marque as moléculas na ordem correta. Desmarcar renumera as seguintes.
    </p>
    <p v-if="erros['payload.correct_order']" class="form-erro" role="alert">
      {{ erros["payload.correct_order"] }}
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
