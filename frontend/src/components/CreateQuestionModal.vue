<script setup>
import { computed, ref, watch } from "vue";
import PopupTemplate from "./PopupTemplate.vue";
import QuestionCommonFields from "./QuestionCommonFields.vue";
import { FORMULARIOS } from "./formularios/registro";
import {
  atualizarQuestao,
  criarQuestao,
  errosPorCampo,
} from "../services/questoes";

const props = defineProps({
  open: { type: Boolean, default: false },
  pacotes: { type: Array, default: () => [] },
  minigames: { type: Array, default: () => [] },
  difficulties: { type: Array, default: () => [] },
  // Questão completa (questoes_obter) para editar; null cria uma nova.
  questao: { type: Object, default: null },
});

const emit = defineEmits(["close", "salvo"]);

const etapa = ref("minigame");
const minigame = ref("");
const pacote = ref(null);
const dificuldade = ref(1);
const justificativa = ref("");
const rascunho = ref(null);
const confirmandoDescarte = ref(false);
const salvando = ref(false);
const erros = ref({});
const erroGeral = ref("");
const estadoInicial = ref("");
// Erros vindos do backend ficam até o próximo salvamento; os locais somem assim que o campo é corrigido.
let chavesDoBackend = new Set();

const minigameSelecionado = computed(() =>
  props.minigames.find((item) => item.value === minigame.value),
);
const nomeMinigame = computed(() => minigameSelecionado.value?.name ?? "");
const formulario = computed(() => FORMULARIOS[minigame.value] ?? null);
const editando = computed(() => props.questao !== null);
const titulo = computed(() =>
  editando.value ? "Editar questão" : "Criar nova questão",
);

// Retrato do que foi preenchido; a Data URI fica de fora para a comparação ser leve.
function retrato() {
  return JSON.stringify(
    {
      rascunho: rascunho.value,
      pacote: pacote.value,
      dificuldade: dificuldade.value,
      justificativa: justificativa.value,
    },
    (chave, valor) => (chave === "data_uri" ? undefined : valor),
  );
}

const alterado = computed(
  () => etapa.value === "formulario" && retrato() !== estadoInicial.value,
);

function reiniciar() {
  confirmandoDescarte.value = false;
  salvando.value = false;
  erros.value = {};
  erroGeral.value = "";
  chavesDoBackend = new Set();

  const questao = props.questao;
  if (questao) {
    // Edição: abre direto no formulário do minigame, já preenchido.
    etapa.value = "formulario";
    minigame.value = questao.minigame_type;
    pacote.value = questao.package?.id ?? null;
    dificuldade.value = questao.difficulty;
    justificativa.value = questao.explanation ?? "";
    rascunho.value = formulario.value?.deQuestao(questao) ?? null;
    estadoInicial.value = retrato();
    return;
  }

  etapa.value = "minigame";
  minigame.value = props.minigames[0]?.value ?? "";
  pacote.value = null;
  dificuldade.value = 1;
  justificativa.value = "";
  rascunho.value = null;
}

function prosseguir() {
  if (!minigame.value) return;
  rascunho.value = formulario.value?.criarRascunho() ?? null;
  etapa.value = "formulario";
  estadoInicial.value = retrato();
}

// Cancelar, Esc e clique fora passam por aqui: só pede confirmação se houver algo a perder.
function pedirFechamento() {
  if (salvando.value) return;
  if (alterado.value) {
    confirmandoDescarte.value = true;
  } else {
    emit("close");
  }
}

function descartar() {
  confirmandoDescarte.value = false;
  emit("close");
}

async function salvar() {
  if (!formulario.value || salvando.value) return;
  erroGeral.value = "";
  chavesDoBackend = new Set();
  erros.value = formulario.value.validar(rascunho.value);
  if (Object.keys(erros.value).length) {
    erroGeral.value = "Corrija os campos destacados.";
    return;
  }

  const dados = {
    minigame_type: minigame.value,
    difficulty: dificuldade.value,
    statement: rascunho.value.enunciado.trim(),
    payload: formulario.value.paraPayload(rascunho.value),
    package_id: pacote.value,
    // O backend recusa texto vazio: justificativa em branco vai como null.
    explanation: justificativa.value.trim() || null,
  };

  salvando.value = true;
  try {
    let questao;
    if (editando.value) {
      // questoes_atualizar substitui tudo: tags e fonte, que o formulário não mostra, vão como estavam.
      dados.tags = props.questao.tags ?? [];
      if (props.questao.source) dados.source = props.questao.source;
      questao = await atualizarQuestao(props.questao.id, dados);
    } else {
      questao = await criarQuestao(dados);
    }
    emit("salvo", questao);
  } catch (falha) {
    // Nada do formulário é apagado: o professor corrige e tenta de novo.
    erros.value = errosPorCampo(falha);
    chavesDoBackend = new Set(Object.keys(erros.value));
    erroGeral.value =
      erros.value.payload ??
      (Object.keys(erros.value).length
        ? "Corrija os campos destacados."
        : falha.message);
  } finally {
    salvando.value = false;
  }
}

watch(retrato, () => {
  if (!formulario.value || !Object.keys(erros.value).length) return;
  const atuais = formulario.value.validar(rascunho.value);
  erros.value = Object.fromEntries(
    Object.entries(erros.value).filter(
      ([chave]) => chave in atuais || chavesDoBackend.has(chave),
    ),
  );
  if (!Object.keys(erros.value).length) erroGeral.value = "";
});

watch(
  () => props.open,
  (aberto) => {
    if (aberto) reiniciar();
  },
  { immediate: true },
);
</script>

<template>
  <PopupTemplate
    :open="open"
    :title="titulo"
    :description="
      etapa === 'minigame'
        ? 'Selecione o minigame para o qual deseja criar uma questão.'
        : `Minigame: ${nomeMinigame}`
    "
    :show-close="false"
    :size="etapa === 'minigame' ? 'medium' : 'form'"
    :content-class="
      etapa === 'minigame'
        ? 'popup-conteudo-formulario'
        : 'popup-conteudo-formulario popup-conteudo-questao'
    "
    @close="pedirFechamento"
  >
    <form
      v-if="etapa === 'minigame'"
      class="questao-etapa1"
      @submit.prevent="prosseguir"
    >
      <label class="sr-only" for="questao-minigame">Minigame</label>
      <select
        id="questao-minigame"
        v-model="minigame"
        class="questao-minigame"
        data-autofocus
      >
        <option v-for="item in minigames" :key="item.value" :value="item.value">
          {{ item.name }}
        </option>
      </select>
      <p
        v-if="minigameSelecionado?.description"
        class="questao-descricao"
        aria-live="polite"
      >
        {{ minigameSelecionado.description }}
      </p>
      <div class="popup-acoes questao-acoes">
        <button
          class="popup-acao popup-acao-cancelar"
          type="button"
          @click="pedirFechamento"
        >
          Cancelar
        </button>
        <button
          class="popup-acao popup-acao-confirmar"
          type="submit"
          :disabled="!minigame"
        >
          Prosseguir
        </button>
      </div>
    </form>

    <template v-else>
      <div class="questao-corpo">
        <component
          :is="formulario.componente"
          v-if="formulario"
          v-model:rascunho="rascunho"
          :erros="erros"
        />
        <p v-else class="questao-pendente">
          {{
            editando
              ? "Este minigame ainda não pode ser editado por aqui."
              : "O formulário deste minigame entra nos próximos blocos."
          }}
        </p>

        <QuestionCommonFields
          v-model:pacote="pacote"
          v-model:dificuldade="dificuldade"
          v-model:justificativa="justificativa"
          :pacotes="pacotes"
          :difficulties="difficulties"
          :erros="erros"
        />
      </div>

      <div class="popup-acoes questao-acoes questao-rodape">
        <p v-if="erroGeral" class="questao-erro" role="alert">
          {{ erroGeral }}
        </p>
        <button
          class="popup-acao popup-acao-cancelar"
          type="button"
          :disabled="salvando"
          @click="pedirFechamento"
        >
          Cancelar
        </button>
        <button
          class="popup-acao popup-acao-confirmar"
          type="button"
          :disabled="!formulario || salvando"
          @click="salvar"
        >
          {{ salvando ? "Salvando..." : "Salvar questão" }}
        </button>
      </div>
    </template>
  </PopupTemplate>

  <PopupTemplate
    :open="confirmandoDescarte"
    title="Descartar alterações?"
    description="O que foi preenchido nesta questão será perdido."
    :show-close="false"
    size="confirm"
    @close="confirmandoDescarte = false"
  >
    <div class="popup-acoes">
      <button
        class="popup-acao popup-acao-cancelar"
        type="button"
        @click="confirmandoDescarte = false"
      >
        Continuar editando
      </button>
      <button
        class="popup-acao popup-acao-descartar"
        type="button"
        @click="descartar"
      >
        Descartar
      </button>
    </div>
  </PopupTemplate>
</template>

<style scoped>
.questao-etapa1 {
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.questao-minigame {
  width: min(100%, 496px);
  height: 74px;
  justify-self: center;
  padding: 0 22px;
  border: 3px solid var(--cor-principal);
  border-radius: 24px;
  color: var(--cor-principal);
  background: var(--cor-superficie);
  font: 800 1.35rem var(--fonte);
  cursor: pointer;
}

.questao-descricao {
  justify-self: center;
  max-width: 496px;
  font-size: 1rem;
  text-align: center;
}

.questao-minigame:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px rgba(0, 142, 21, 0.16);
}

.questao-acoes {
  justify-content: space-between;
  margin-top: 10px;
}

.questao-acoes .popup-acao {
  min-width: 226px;
  min-height: 66px;
  border-radius: 22px;
  font-size: 1.3rem;
}

.questao-corpo {
  display: grid;
  flex: 1;
  min-height: 0;
  align-content: start;
  gap: 18px;
  padding: 6px 4px 12px;
  overflow-y: auto;
}

.questao-pendente {
  padding: 40px 0;
  text-align: center;
}

.questao-rodape {
  justify-content: flex-end;
  align-items: center;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--cor-linha);
}

.questao-erro {
  flex: 1;
  color: #d11a1a !important;
  font-size: 1rem !important;
  font-weight: 700;
}

.popup-acao-descartar {
  border-color: #d11a1a;
  color: var(--cor-texto-claro);
  background: #d11a1a;
}

.popup-acao:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
