<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { Plus } from "@lucide/vue";
import PopupTemplate from "./PopupTemplate.vue";
import PackageCard from "./PackageCard.vue";
import QuestionCard from "./QuestionCard.vue";
import CreatePackageModal from "./CreatePackageModal.vue";
import CreateQuestionModal from "./CreateQuestionModal.vue";
import { useBibliotecaImagens } from "../composables/useBibliotecaImagens";
import {
  listarPacotes,
  listarQuestoes,
  obterMetadados,
  obterQuestao,
  removerPacote,
  removerQuestao,
} from "../services/questoes";

const POR_PAGINA = 50;
const ESPERA_BUSCA_MS = 300;

const props = defineProps({
  open: { type: Boolean, default: false },
});

const emit = defineEmits(["close"]);

const busca = ref("");
const pacotes = ref([]);
const metadados = ref({ minigames: [], difficulties: [] });
const carregando = ref(false);
const erro = ref("");

const questoes = ref([]);
const totalQuestoes = ref(0);
const carregandoQuestoes = ref(false);
const erroQuestoes = ref("");

const criandoPacote = ref(false);
const criandoQuestao = ref(false);
// Questão completa aberta para edição; null quando o modal está criando.
const questaoEditada = ref(null);
const abrindoEdicao = ref(false);
const erroEdicao = ref("");

const pacoteParaRemover = ref(null);
const questaoParaRemover = ref(null);
const removendo = ref(false);
const erroRemocao = ref("");
const tituloRemocao = computed(() =>
  pacoteParaRemover.value
    ? `Remover o pacote "${pacoteParaRemover.value.name}"?`
    : "Remover esta questão?",
);
const descricaoRemocao = computed(() =>
  pacoteParaRemover.value
    ? "As questões dele continuam no banco, sem pacote."
    : "A remoção é definitiva. Imagens importadas que só ela usa também são apagadas.",
);

const biblioteca = useBibliotecaImagens();
// Miniaturas: a listagem traz só o id da imagem; a Data URI vem da biblioteca já carregada.
const miniaturas = computed(
  () =>
    new Map(
      biblioteca.imagens.value.map((imagem) => [imagem.id, imagem.data_uri]),
    ),
);

// Ignora maiúsculas e acentos: "quimica" encontra "Química".
function normalizar(texto) {
  return texto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

const pacotesFiltrados = computed(() => {
  const termo = normalizar(busca.value);
  if (!termo) return pacotes.value;
  return pacotes.value.filter((pacote) =>
    normalizar(pacote.name).includes(termo),
  );
});

const temMaisQuestoes = computed(
  () => questoes.value.length < totalQuestoes.value,
);
const listaVazia = computed(
  () => !pacotesFiltrados.value.length && !questoes.value.length,
);

async function carregarPacotes() {
  carregando.value = true;
  erro.value = "";
  try {
    const [dadosMetadados, dadosPacotes] = await Promise.all([
      obterMetadados(),
      listarPacotes(),
    ]);
    metadados.value = dadosMetadados;
    pacotes.value = dadosPacotes;
  } catch (falha) {
    erro.value = falha.message;
  } finally {
    carregando.value = false;
  }
}

// A busca de questões é feita pelo backend (enunciado ou nome do minijogo).
async function carregarQuestoes({ continuar = false } = {}) {
  carregandoQuestoes.value = true;
  erroQuestoes.value = "";
  const filtros = {
    limite: POR_PAGINA,
    deslocamento: continuar ? questoes.value.length : 0,
  };
  if (busca.value.trim()) filtros.busca = busca.value.trim();
  try {
    const resultado = await listarQuestoes(filtros);
    questoes.value = continuar
      ? [...questoes.value, ...resultado.items]
      : resultado.items;
    totalQuestoes.value = resultado.total;
  } catch (falha) {
    erroQuestoes.value = falha.message;
  } finally {
    carregandoQuestoes.value = false;
  }
}

function carregar() {
  biblioteca.carregar();
  return Promise.all([carregarPacotes(), carregarQuestoes()]);
}

async function aoCriarPacote() {
  criandoPacote.value = false;
  await carregar();
}

function novaQuestao() {
  questaoEditada.value = null;
  criandoQuestao.value = true;
}

// A listagem não traz o payload nem as imagens; a edição busca a questão completa.
async function editarQuestao(questao) {
  if (abrindoEdicao.value) return;
  abrindoEdicao.value = true;
  erroEdicao.value = "";
  try {
    questaoEditada.value = await obterQuestao(questao.id);
    criandoQuestao.value = true;
  } catch (falha) {
    erroEdicao.value = falha.message;
  } finally {
    abrindoEdicao.value = false;
  }
}

function fecharQuestao() {
  criandoQuestao.value = false;
  questaoEditada.value = null;
}

async function aoSalvarQuestao() {
  fecharQuestao();
  await carregar();
}

function pedirRemocaoPacote(pacote) {
  erroRemocao.value = "";
  pacoteParaRemover.value = pacote;
}

function pedirRemocaoQuestao(questao) {
  erroRemocao.value = "";
  questaoParaRemover.value = questao;
}

function cancelarRemocao() {
  if (removendo.value) return;
  pacoteParaRemover.value = null;
  questaoParaRemover.value = null;
}

async function confirmarRemocao() {
  removendo.value = true;
  erroRemocao.value = "";
  try {
    if (pacoteParaRemover.value) {
      await removerPacote(pacoteParaRemover.value.id);
    } else {
      await removerQuestao(questaoParaRemover.value.id);
      // A remoção pode ter apagado imagens que só ela usava.
      biblioteca.carregar(true);
    }
    pacoteParaRemover.value = null;
    questaoParaRemover.value = null;
    await carregar();
  } catch (falha) {
    erroRemocao.value = falha.message;
  } finally {
    removendo.value = false;
  }
}

let esperaBusca = null;
watch(busca, () => {
  if (!props.open) return;
  clearTimeout(esperaBusca);
  esperaBusca = setTimeout(() => carregarQuestoes(), ESPERA_BUSCA_MS);
});

onBeforeUnmount(() => clearTimeout(esperaBusca));

watch(
  () => props.open,
  (aberto) => {
    if (aberto) {
      busca.value = "";
      carregar();
    } else {
      // Os modais filhos só existem com o Banco aberto; sem isso, reabrir o Banco os deixaria por baixo.
      clearTimeout(esperaBusca);
      criandoPacote.value = false;
      criandoQuestao.value = false;
      questaoEditada.value = null;
      erroEdicao.value = "";
      pacoteParaRemover.value = null;
      questaoParaRemover.value = null;
    }
  },
  { immediate: true },
);
</script>

<template>
  <PopupTemplate
    v-model="busca"
    :open="open"
    title="Banco de questões"
    hide-title
    content-class="popup-conteudo-lista"
    search-placeholder="Pesquisar questão/pacote..."
    @close="emit('close')"
  >
    <div class="banco-acoes">
      <button class="banco-criar" type="button" @click="novaQuestao">
        <Plus aria-hidden="true" />
        Criar questão
      </button>
      <button class="banco-criar" type="button" @click="criandoPacote = true">
        <Plus aria-hidden="true" />
        Criar pacote
      </button>
    </div>

    <p v-if="carregando" class="banco-aviso" role="status">Carregando...</p>

    <div v-else-if="erro" class="banco-aviso" role="alert">
      <p>Não foi possível carregar o banco de questões. {{ erro }}</p>
      <button
        class="popup-acao popup-acao-cancelar"
        type="button"
        @click="carregar"
      >
        Tentar novamente
      </button>
    </div>

    <template v-else>
      <PackageCard
        v-for="pacote in pacotesFiltrados"
        :key="pacote.id"
        :pacote="pacote"
        :minigames="metadados.minigames"
        :difficulties="metadados.difficulties"
        @remover="pedirRemocaoPacote"
      />

      <h2 v-if="questoes.length" class="banco-secao">Questões</h2>
      <p v-if="erroEdicao" class="banco-erro" role="alert">
        Não foi possível abrir a questão para edição. {{ erroEdicao }}
      </p>
      <QuestionCard
        v-for="questao in questoes"
        :key="questao.id"
        :questao="questao"
        :imagem="miniaturas.get(questao.preview_asset?.id) ?? ''"
        @editar="editarQuestao"
        @remover="pedirRemocaoQuestao"
      />

      <div v-if="erroQuestoes" class="banco-aviso" role="alert">
        <p>Não foi possível carregar as questões. {{ erroQuestoes }}</p>
        <button
          class="popup-acao popup-acao-cancelar"
          type="button"
          @click="carregarQuestoes()"
        >
          Tentar novamente
        </button>
      </div>
      <p v-else-if="carregandoQuestoes" class="banco-aviso" role="status">
        Carregando questões...
      </p>
      <button
        v-else-if="temMaisQuestoes"
        class="popup-acao popup-acao-cancelar banco-mais"
        type="button"
        @click="carregarQuestoes({ continuar: true })"
      >
        Carregar mais questões
      </button>
      <p v-else class="banco-aviso">
        {{
          listaVazia
            ? "Nenhuma questão ou pacote encontrado"
            : "Fim da lista de questões/pacotes"
        }}
      </p>
    </template>
  </PopupTemplate>

  <CreatePackageModal
    :open="criandoPacote"
    @close="criandoPacote = false"
    @criado="aoCriarPacote"
  />

  <CreateQuestionModal
    :open="criandoQuestao"
    :questao="questaoEditada"
    :pacotes="pacotes"
    :minigames="metadados.minigames"
    :difficulties="metadados.difficulties"
    @close="fecharQuestao"
    @salvo="aoSalvarQuestao"
  />

  <PopupTemplate
    :open="pacoteParaRemover !== null || questaoParaRemover !== null"
    :title="tituloRemocao"
    :description="descricaoRemocao"
    :show-close="false"
    size="confirm"
    @close="cancelarRemocao"
  >
    <p v-if="erroRemocao" class="banco-erro" role="alert">{{ erroRemocao }}</p>
    <div class="popup-acoes">
      <button
        class="popup-acao popup-acao-cancelar"
        type="button"
        :disabled="removendo"
        @click="cancelarRemocao"
      >
        Cancelar
      </button>
      <button
        class="popup-acao popup-acao-remover"
        type="button"
        :disabled="removendo"
        @click="confirmarRemocao"
      >
        {{ removendo ? "Removendo..." : "Remover" }}
      </button>
    </div>
  </PopupTemplate>
</template>

<style scoped>
.banco-acoes {
  display: flex;
  gap: 12px;
}

.banco-criar {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  gap: 10px;
  padding: 0 22px;
  border: 3px solid var(--cor-principal);
  border-radius: 999px;
  color: var(--cor-principal);
  background: var(--cor-superficie);
  font: 800 1.3rem var(--fonte);
  cursor: pointer;
}

.banco-criar:hover,
.banco-criar:focus-visible {
  background: rgba(0, 142, 21, 0.08);
}

.banco-criar svg {
  width: 26px;
  height: 26px;
  stroke-width: 4;
}

.banco-secao {
  margin-top: 6px;
  color: var(--cor-texto-secundario);
  font-size: 1.2rem;
}

.banco-mais {
  justify-self: center;
  padding: 0 22px;
}

.banco-aviso {
  display: grid;
  justify-items: center;
  gap: 12px;
  padding: 12px;
  color: var(--cor-texto-secundario);
  font-weight: 700;
  text-align: center;
}

.banco-erro {
  color: #d11a1a;
  font-weight: 700;
}

.popup-acao-remover {
  border-color: #d11a1a;
  color: var(--cor-texto-claro);
  background: #d11a1a;
}

.popup-acao:disabled {
  opacity: 0.6;
  cursor: wait;
}
</style>
