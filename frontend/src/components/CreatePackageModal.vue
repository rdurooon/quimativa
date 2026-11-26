<script setup>
import { computed, ref, watch } from "vue";
import PopupTemplate from "./PopupTemplate.vue";
import { criarPacote, errosPorCampo } from "../services/questoes";

const props = defineProps({
  open: { type: Boolean, default: false },
});

const emit = defineEmits(["close", "criado"]);

const nome = ref("");
const salvando = ref(false);
const erro = ref("");
const podeCriar = computed(() => nome.value.trim() !== "" && !salvando.value);

async function criar() {
  if (!podeCriar.value) return;
  salvando.value = true;
  erro.value = "";
  try {
    const pacote = await criarPacote(nome.value.trim());
    emit("criado", pacote);
  } catch (falha) {
    // Mantém o nome digitado para o usuário corrigir.
    erro.value = errosPorCampo(falha).name ?? falha.message;
  } finally {
    salvando.value = false;
  }
}

function cancelar() {
  if (!salvando.value) emit("close");
}

watch(
  () => props.open,
  (aberto) => {
    if (aberto) {
      nome.value = "";
      erro.value = "";
    }
  },
);
</script>

<template>
  <PopupTemplate
    :open="open"
    title="Criar novo pacote"
    description="Dê nome ao novo pacote de questões."
    :show-close="false"
    size="medium"
    content-class="popup-conteudo-formulario"
    @close="cancelar"
  >
    <form class="pacote-form" @submit.prevent="criar">
      <label class="sr-only" for="novo-pacote-nome">Nome do pacote</label>
      <input
        id="novo-pacote-nome"
        v-model="nome"
        class="pacote-form-campo"
        :class="{ 'pacote-form-campo-erro': erro }"
        type="text"
        placeholder="Novo pacote..."
        maxlength="120"
        autocomplete="off"
        data-autofocus
        :aria-invalid="erro ? 'true' : 'false'"
        :aria-describedby="erro ? 'novo-pacote-erro' : undefined"
        @input="erro = ''"
      />
      <p
        v-if="erro"
        id="novo-pacote-erro"
        class="pacote-form-erro"
        role="alert"
      >
        {{ erro }}
      </p>

      <div class="popup-acoes pacote-form-acoes">
        <button
          class="popup-acao popup-acao-cancelar"
          type="button"
          :disabled="salvando"
          @click="cancelar"
        >
          Cancelar
        </button>
        <button
          class="popup-acao popup-acao-confirmar"
          type="submit"
          :disabled="!podeCriar"
        >
          {{ salvando ? "Criando..." : "Criar" }}
        </button>
      </div>
    </form>
  </PopupTemplate>
</template>

<style scoped>
.pacote-form {
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.pacote-form-campo {
  width: min(100%, 496px);
  height: 74px;
  justify-self: center;
  padding: 0 22px;
  border: 3px solid var(--cor-principal);
  border-radius: 24px;
  color: var(--cor-texto);
  font: 700 1.6rem var(--fonte);
}

.pacote-form-campo::placeholder {
  color: #5cb86a;
}

.pacote-form-campo:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(0, 142, 21, 0.16);
}

.pacote-form-campo-erro {
  border-color: #d11a1a;
}

.pacote-form-erro {
  justify-self: center;
  color: #d11a1a;
  font-weight: 700;
}

.pacote-form-acoes {
  justify-content: space-between;
  margin-top: 10px;
}

.pacote-form-acoes .popup-acao {
  min-width: 226px;
  min-height: 66px;
  border-radius: 22px;
  font-size: 1.3rem;
}

.popup-acao:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
