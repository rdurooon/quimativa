<script setup>
const pacote = defineModel("pacote", { default: null });
const dificuldade = defineModel("dificuldade", { default: 1 });

const justificativa = defineModel("justificativa", { default: "" });

const LIMITE_JUSTIFICATIVA = 2000;

defineProps({
  pacotes: { type: Array, default: () => [] },
  difficulties: { type: Array, default: () => [] },
  erros: { type: Object, default: () => ({}) },
});
</script>

<template>
  <div class="campos-comuns">
    <label class="campo-justificativa">
      <p v-if="erros.explanation" class="campo-erro" role="alert">
        {{ erros.explanation }}
      </p>
      <span class="campo-rotulo">Justificativa <small>(opcional)</small></span>
      <textarea
        v-model="justificativa"
        rows="3"
        :maxlength="LIMITE_JUSTIFICATIVA"
        placeholder="Explique por que a resposta está correta..."
      />
      <small class="campo-contador"
        >{{ justificativa.length }}/{{ LIMITE_JUSTIFICATIVA }}</small
      >
    </label>
    <label class="campo-linha">
      <span class="campo-rotulo">Pacote:</span>
      <select v-model="pacote" class="campo-pacote">
        <option :value="null">Nenhum</option>
        <option v-for="item in pacotes" :key="item.id" :value="item.id">
          {{ item.name }}
        </option>
      </select>
    </label>

    <fieldset class="campo-linha">
      <legend class="campo-rotulo">Dificuldade:</legend>
      <div class="dificuldades" role="radiogroup">
        <label
          v-for="item in difficulties"
          :key="item.value"
          class="dificuldade"
          :class="{ 'dificuldade-ativa': dificuldade === item.value }"
        >
          <input
            v-model="dificuldade"
            class="sr-only"
            type="radio"
            name="dificuldade"
            :value="item.value"
          />
          {{ item.name }}
        </label>
      </div>
    </fieldset>
  </div>
</template>

<style scoped>
.campos-comuns {
  display: grid;
  gap: 14px;
}

.campo-justificativa {
  display: grid;
  gap: 6px;
}

.campo-justificativa small {
  font-weight: 600;
}

.campo-justificativa textarea {
  min-height: 92px;
  padding: 12px 16px;
  border: 3px solid #9ba5a0;
  border-radius: 16px;
  color: var(--cor-texto);
  font: 600 1.05rem var(--fonte);
  resize: vertical;
}

.campo-justificativa textarea:focus-visible {
  outline: none;
  border-color: var(--cor-principal);
}

.campo-contador {
  justify-self: end;
  color: var(--cor-texto-secundario);
}

.campo-erro {
  color: #d11a1a !important;
  font-size: 0.95rem !important;
  font-weight: 700;
}

.campo-linha {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
}

.campo-rotulo {
  float: left;
  padding: 0;
  color: var(--cor-texto-secundario);
  font-size: 1.25rem;
  font-weight: 800;
}

.campo-pacote {
  min-width: 284px;
  height: 46px;
  padding: 0 14px;
  border: 3px solid #9ba5a0;
  border-radius: 16px;
  color: var(--cor-texto-secundario);
  background: var(--cor-superficie);
  font: 800 1.2rem var(--fonte);
}

.campo-pacote:focus-visible {
  outline: none;
  border-color: var(--cor-principal);
}

.dificuldades {
  display: flex;
  overflow: hidden;
  border: 3px solid #9ba5a0;
  border-radius: 16px;
}

.dificuldade {
  min-width: 136px;
  padding: 8px 16px;
  color: var(--cor-texto-secundario);
  font-size: 1.2rem;
  font-weight: 800;
  text-align: center;
  cursor: pointer;
}

.dificuldade + .dificuldade {
  border-left: 3px solid #9ba5a0;
}

.dificuldade-ativa {
  color: var(--cor-texto-claro);
  background: var(--cor-principal);
}

.dificuldade:focus-within {
  box-shadow: inset 0 0 0 3px rgba(0, 107, 16, 0.5);
}
</style>
