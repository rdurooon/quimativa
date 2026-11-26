<script setup>
import { Image, Type } from "@lucide/vue";
import AssetPicker from "../AssetPicker.vue";
import MarcadorCorreta from "./MarcadorCorreta.vue";

// Grade 2×2 compartilhada. A regra de seleção fica no formulário, que informa o estado de cada marcador.
const cartas = defineModel("cartas", { required: true });

defineProps({
  erros: { type: Object, default: () => ({}) },
  // Ordem das funções usa só imagens, sem texto complementar.
  somenteImagem: { type: Boolean, default: false },
  marcado: { type: Function, required: true },
  numero: { type: Function, default: () => null },
  desabilitado: { type: Function, default: () => false },
  rotuloMarcador: { type: Function, required: true },
  prefixoErro: { type: String, default: "payload.cards" },
});

defineEmits(["alternar"]);
</script>

<template>
  <div class="grade">
    <div v-for="(carta, indice) in cartas" :key="carta.id" class="grade-bloco">
      <div
        class="carta"
        :class="{
          'carta-marcada': marcado(carta.id),
          'carta-invalida': erros[`${prefixoErro}.${indice}`],
        }"
      >
        <div class="carta-topo">
          <div
            v-if="!somenteImagem"
            class="carta-tipo"
            role="group"
            :aria-label="`Conteúdo da carta ${indice + 1}`"
          >
            <button
              type="button"
              :class="{ ativo: carta.tipo === 'imagem' }"
              :aria-pressed="carta.tipo === 'imagem' ? 'true' : 'false'"
              title="Usar imagem"
              @click="carta.tipo = 'imagem'"
            >
              <Image aria-hidden="true" />
              <span class="sr-only">Imagem</span>
            </button>
            <button
              type="button"
              :class="{ ativo: carta.tipo === 'texto' }"
              :aria-pressed="carta.tipo === 'texto' ? 'true' : 'false'"
              title="Usar texto"
              @click="carta.tipo = 'texto'"
            >
              <Type aria-hidden="true" />
              <span class="sr-only">Texto</span>
            </button>
          </div>
          <MarcadorCorreta
            class="carta-marcador"
            :marcado="marcado(carta.id)"
            :numero="numero(carta.id)"
            :desabilitado="desabilitado(carta.id)"
            :rotulo="rotuloMarcador(carta.id, indice)"
            @alternar="$emit('alternar', carta.id)"
          />
        </div>

        <div class="carta-corpo">
          <AssetPicker
            v-if="somenteImagem || carta.tipo === 'imagem'"
            v-model="carta.imagem"
            compacto
            rotulo="Adicionar imagem"
            :invalido="Boolean(erros[`${prefixoErro}.${indice}`])"
          />
          <div v-else class="carta-texto-caixa">
            <textarea
              v-model="carta.texto"
              class="carta-texto"
              maxlength="200"
              rows="1"
              placeholder="Texto da carta..."
              :aria-label="`Texto principal da carta ${indice + 1}`"
            />
          </div>
        </div>

        <input
          v-if="!somenteImagem"
          v-model="carta.complemento"
          class="carta-complemento"
          type="text"
          maxlength="200"
          placeholder="Texto complementar (opcional)"
          :aria-label="`Texto complementar da carta ${indice + 1}`"
        />
      </div>
      <p
        v-if="erros[`${prefixoErro}.${indice}`]"
        class="grade-erro"
        role="alert"
      >
        {{ erros[`${prefixoErro}.${indice}`] }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.grade {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  width: min(100%, 680px);
  justify-self: center;
}

.grade-bloco {
  display: grid;
  gap: 4px;
}

.carta {
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 8px;
  height: 250px;
  padding: 8px;
  border: 3px solid #9ba5a0;
  border-radius: 18px;
  background: var(--cor-superficie);
}

.carta-marcada {
  border-color: var(--cor-principal);
  box-shadow: 0 0 0 2px var(--cor-principal);
}

.carta-invalida {
  border-color: #d11a1a;
}

.carta-topo {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.carta-marcador {
  margin-left: auto;
}

.carta-tipo {
  display: flex;
  overflow: hidden;
  border: 2px solid #9ba5a0;
  border-radius: 12px;
}

.carta-tipo button {
  display: grid;
  width: 40px;
  height: 34px;
  place-items: center;
  border: 0;
  color: var(--cor-texto-secundario);
  background: var(--cor-superficie);
  cursor: pointer;
}

.carta-tipo button + button {
  border-left: 2px solid #9ba5a0;
}

.carta-tipo button.ativo {
  color: var(--cor-texto-claro);
  background: var(--cor-principal);
}

.carta-tipo button:focus-visible {
  outline: none;
  box-shadow: inset 0 0 0 3px rgba(0, 107, 16, 0.5);
}

.carta-tipo svg {
  width: 20px;
  height: 20px;
}

.carta-corpo {
  display: grid;
  min-height: 0;
}

/* A caixa centraliza; o textarea cresce com o texto (field-sizing), como a carta aparece no jogo. */
.carta-texto-caixa {
  display: flex;
  min-height: 0;
  align-items: center;
  padding: 8px;
  border: 2px dashed #9ba5a0;
  border-radius: 12px;
}

.carta-texto-caixa:focus-within,
.carta-complemento:focus-visible {
  outline: none;
  border-color: var(--cor-principal);
}

.carta-texto {
  width: 100%;
  max-height: 100%;
  border: 0;
  color: var(--cor-texto);
  background: transparent;
  font: 800 1.3rem var(--fonte);
  text-align: center;
  field-sizing: content;
  resize: none;
}

.carta-texto:focus {
  outline: none;
}

.carta-complemento {
  height: 34px;
  padding: 0 10px;
  border: 2px solid #d3dbd6;
  border-radius: 10px;
  color: var(--cor-texto-secundario);
  font: 600 0.9rem var(--fonte);
}

.grade-erro {
  color: #d11a1a !important;
  font-size: 0.95rem !important;
  font-weight: 700;
  text-align: center;
}
</style>
