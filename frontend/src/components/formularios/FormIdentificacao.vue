<script setup>
import { computed, watch } from "vue";
import { Check } from "@lucide/vue";
import AssetPicker from "../AssetPicker.vue";

const rascunho = defineModel("rascunho", { required: true });

defineProps({
  erros: { type: Object, default: () => ({}) },
});

const regioes = computed(() => rascunho.value.imagem?.region_ids ?? []);

// Ao trocar a imagem, a região antiga pode não existir mais; com uma única região, ela já vem escolhida.
watch(
  () => rascunho.value.imagem?.id,
  () => {
    if (regioes.value.includes(rascunho.value.regiao)) return;
    rascunho.value.regiao = regioes.value.length === 1 ? regioes.value[0] : "";
  },
);
</script>

<template>
  <div class="form-identificacao">
    <div class="form-imagem">
      <AssetPicker
        v-model="rascunho.imagem"
        :regiao-destacada="rascunho.regiao"
        :invalido="Boolean(erros['payload.molecule_asset_id'])"
      />
    </div>
    <p v-if="erros['payload.molecule_asset_id']" class="form-erro" role="alert">
      {{ erros["payload.molecule_asset_id"] }}
    </p>

    <div v-if="rascunho.imagem" class="form-regiao">
      <label v-if="regioes.length" class="form-regiao-campo">
        <span>Região destacada:</span>
        <select
          v-model="rascunho.regiao"
          :aria-invalid="
            erros['payload.highlight.region_id'] ? 'true' : 'false'
          "
        >
          <option value="" disabled>Escolha a região</option>
          <option v-for="regiao in regioes" :key="regiao" :value="regiao">
            {{ regiao }}
          </option>
        </select>
      </label>
      <p v-else class="form-erro" role="alert">
        Esta imagem não tem regiões marcadas. Use um SVG com o grupo funcional
        identificado por um id.
      </p>
      <p
        v-if="erros['payload.highlight.region_id']"
        class="form-erro"
        role="alert"
      >
        {{ erros["payload.highlight.region_id"] }}
      </p>
    </div>

    <label class="sr-only" for="identificacao-enunciado">Enunciado</label>
    <input
      id="identificacao-enunciado"
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

    <fieldset class="form-alternativas">
      <legend class="sr-only">Alternativas (marque a correta)</legend>
      <div
        v-for="(alternativa, indice) in rascunho.alternativas"
        :key="alternativa.id"
        class="form-alternativa-bloco"
      >
        <div
          class="form-alternativa"
          :class="{
            'form-alternativa-correta': rascunho.correta === alternativa.id,
            'form-campo-invalido':
              erros[`payload.alternatives.${indice}.label`],
          }"
        >
          <input
            v-model="alternativa.label"
            type="text"
            maxlength="200"
            placeholder="Adicionar texto..."
            :aria-label="`Alternativa ${alternativa.id}`"
          />
          <label
            class="form-correta"
            :title="`Marcar ${alternativa.id} como correta`"
          >
            <input
              v-model="rascunho.correta"
              class="sr-only"
              type="radio"
              name="identificacao-correta"
              :value="alternativa.id"
              :aria-label="`Alternativa ${alternativa.id} é a correta`"
            />
            <Check aria-hidden="true" />
          </label>
        </div>
        <p
          v-if="erros[`payload.alternatives.${indice}.label`]"
          class="form-erro"
          role="alert"
        >
          {{ erros[`payload.alternatives.${indice}.label`] }}
        </p>
      </div>
    </fieldset>
    <p
      v-if="erros['payload.correct_alternative_id']"
      class="form-erro"
      role="alert"
    >
      {{ erros["payload.correct_alternative_id"] }}
    </p>
  </div>
</template>

<style scoped>
.form-identificacao {
  display: grid;
  gap: 12px;
}

.form-imagem {
  width: min(100%, 510px);
  height: 300px;
  justify-self: center;
}

.form-regiao {
  display: grid;
  justify-items: center;
  gap: 6px;
}

.form-regiao-campo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--cor-texto-secundario);
  font-weight: 800;
}

.form-regiao-campo select {
  min-width: 220px;
  height: 40px;
  padding: 0 12px;
  border: 3px solid #9ba5a0;
  border-radius: 14px;
  color: var(--cor-texto);
  background: var(--cor-superficie);
  font: 700 1rem var(--fonte);
}

.form-enunciado,
.form-alternativa {
  border: 3px solid #9ba5a0;
  border-radius: 22px;
  background: var(--cor-superficie);
}

.form-enunciado {
  width: min(100%, 620px);
  height: 48px;
  justify-self: center;
  padding: 0 16px;
  color: var(--cor-texto);
  font: 700 1.2rem var(--fonte);
}

.form-enunciado:focus-visible,
.form-alternativa:focus-within {
  outline: none;
  border-color: var(--cor-principal);
}

.form-alternativas {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 40px;
  width: min(100%, 640px);
  justify-self: center;
  margin: 0;
  padding: 0;
  border: 0;
}

.form-alternativa-bloco {
  display: grid;
  gap: 4px;
}

.form-alternativa {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 62px;
  padding: 0 8px 0 12px;
}

.form-alternativa input[type="text"] {
  flex: 1;
  min-width: 0;
  border: 0;
  color: var(--cor-texto);
  background: transparent;
  font: 700 1.15rem var(--fonte);
}

.form-alternativa input[type="text"]:focus {
  outline: none;
}

.form-correta {
  display: grid;
  width: 44px;
  height: 44px;
  flex: none;
  place-items: center;
  border: 2px solid #9ba5a0;
  border-radius: 50%;
  color: #9ba5a0;
  cursor: pointer;
}

.form-correta svg {
  width: 26px;
  height: 26px;
}

.form-correta:focus-within {
  box-shadow: 0 0 0 3px rgba(0, 142, 21, 0.25);
}

.form-alternativa-correta {
  border-color: var(--cor-principal);
}

.form-alternativa-correta .form-correta {
  border-color: var(--cor-principal);
  color: var(--cor-principal);
  background: rgba(0, 142, 21, 0.08);
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
