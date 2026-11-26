<script setup>
import AssetPicker from "../AssetPicker.vue";
import MarcadorCorreta from "./MarcadorCorreta.vue";

const rascunho = defineModel("rascunho", { required: true });

defineProps({
  erros: { type: Object, default: () => ({}) },
});

// Marcar uma caixa desmarca a outra; clicar de novo na marcada a desmarca.
function alternar(id) {
  rascunho.value.correta = rascunho.value.correta === id ? null : id;
}
</script>

<template>
  <div class="form-diferenca">
    <label class="sr-only" for="diferenca-enunciado">Enunciado</label>
    <input
      id="diferenca-enunciado"
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

    <div class="form-caixas">
      <div
        v-for="(molecula, indice) in rascunho.moleculas"
        :key="molecula.id"
        class="form-caixa-bloco"
      >
        <div
          class="form-caixa"
          :class="{ 'form-caixa-correta': rascunho.correta === molecula.id }"
        >
          <AssetPicker
            v-model="molecula.imagem"
            :invalido="Boolean(erros[`payload.molecules.${indice}.asset_id`])"
          />
          <MarcadorCorreta
            class="form-marcador"
            :marcado="rascunho.correta === molecula.id"
            :rotulo="`Molécula ${indice + 1} é a correta`"
            @alternar="alternar(molecula.id)"
          />
        </div>
        <p
          v-if="erros[`payload.molecules.${indice}.asset_id`]"
          class="form-erro"
          role="alert"
        >
          {{ erros[`payload.molecules.${indice}.asset_id`] }}
        </p>
      </div>
    </div>
    <p
      v-if="erros['payload.correct_molecule_id']"
      class="form-erro"
      role="alert"
    >
      {{ erros["payload.correct_molecule_id"] }}
    </p>
  </div>
</template>

<style scoped>
.form-diferenca {
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

.form-caixas {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  width: min(100%, 680px);
  justify-self: center;
}

.form-caixa-bloco {
  display: grid;
  gap: 4px;
}

.form-caixa {
  position: relative;
  height: 260px;
  border-radius: 16px;
}

.form-caixa-correta {
  box-shadow: 0 0 0 3px var(--cor-principal);
}

.form-marcador {
  position: absolute;
  top: 8px;
  right: 8px;
}

.form-campo-invalido {
  border-color: #d11a1a;
}

.form-erro {
  color: #d11a1a !important;
  font-size: 0.95rem !important;
  font-weight: 700;
  text-align: center;
}
</style>
