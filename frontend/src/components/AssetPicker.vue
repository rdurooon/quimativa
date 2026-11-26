<script setup>
import { computed, ref } from "vue";
import { ImagePlus, RefreshCcw, Upload, X } from "@lucide/vue";
import PopupTemplate from "./PopupTemplate.vue";
import { useBibliotecaImagens } from "../composables/useBibliotecaImagens";
import { destacarRegiao } from "../utils/svgDestaque";

// Valor: a imagem escolhida ({ id, name, data_uri, region_ids, ... }) ou null.
const imagem = defineModel({ default: null });

const props = defineProps({
  rotulo: { type: String, default: "Adicionar ou selecionar imagem" },
  regiaoDestacada: { type: String, default: "" },
  compacto: { type: Boolean, default: false },
  invalido: { type: Boolean, default: false },
});

const { imagens, carregando, erro, carregar, importar } =
  useBibliotecaImagens();

const galeriaAberta = ref(false);
const filtro = ref("");
const importando = ref(false);
const erroImportacao = ref("");

const previa = computed(() =>
  destacarRegiao(imagem.value?.data_uri, props.regiaoDestacada),
);

const imagensFiltradas = computed(() => {
  const termo = filtro.value.trim().toLowerCase();
  if (!termo) return imagens.value;
  return imagens.value.filter((item) =>
    (item.name ?? item.id).toLowerCase().includes(termo),
  );
});

function abrirGaleria() {
  filtro.value = "";
  erroImportacao.value = "";
  galeriaAberta.value = true;
  carregar();
}

function escolher(item) {
  imagem.value = item;
  galeriaAberta.value = false;
}

async function aoEscolherArquivo(evento) {
  const [selecionado] = evento.target.files ?? [];
  evento.target.value = "";
  if (!selecionado) return;
  importando.value = true;
  erroImportacao.value = "";
  try {
    escolher(await importar(selecionado));
  } catch (falha) {
    erroImportacao.value = falha.detalhes?.[0]?.mensagem ?? falha.message;
  } finally {
    importando.value = false;
  }
}
</script>

<template>
  <div
    class="seletor"
    :class="{ 'seletor-compacto': compacto, 'seletor-invalido': invalido }"
  >
    <button
      v-if="!imagem"
      class="seletor-vazio"
      type="button"
      :aria-invalid="invalido ? 'true' : undefined"
      @click="abrirGaleria"
    >
      <ImagePlus aria-hidden="true" />
      <span>{{ rotulo }}</span>
    </button>

    <figure v-else class="seletor-previa">
      <img :src="previa" :alt="imagem.name ?? 'Imagem selecionada'" />
      <figcaption class="sr-only">{{ imagem.name }}</figcaption>
      <div class="seletor-acoes">
        <button
          type="button"
          :aria-label="`Trocar imagem ${imagem.name ?? ''}`"
          @click="abrirGaleria"
        >
          <RefreshCcw aria-hidden="true" />
          <span v-if="!compacto">Trocar</span>
        </button>
        <button
          type="button"
          :aria-label="`Remover imagem ${imagem.name ?? ''}`"
          @click="imagem = null"
        >
          <X aria-hidden="true" />
          <span v-if="!compacto">Remover</span>
        </button>
      </div>
    </figure>
  </div>

  <PopupTemplate
    :open="galeriaAberta"
    title="Selecionar imagem"
    description="Importe um arquivo SVG ou escolha uma imagem já cadastrada."
    size="form"
    content-class="popup-conteudo-formulario popup-conteudo-questao"
    @close="galeriaAberta = false"
  >
    <div class="galeria-topo">
      <label
        class="galeria-importar"
        :class="{ 'galeria-importar-ocupado': importando }"
      >
        <Upload aria-hidden="true" />
        {{ importando ? "Importando..." : "Importar arquivo SVG" }}
        <input
          class="sr-only"
          type="file"
          accept=".svg,image/svg+xml"
          :disabled="importando"
          data-autofocus
          @change="aoEscolherArquivo"
        />
      </label>
      <label class="galeria-filtro">
        <span class="sr-only">Filtrar imagens pelo nome</span>
        <input
          v-model="filtro"
          type="search"
          placeholder="Filtrar pelo nome..."
        />
      </label>
    </div>
    <p v-if="erroImportacao" class="galeria-erro" role="alert">
      {{ erroImportacao }}
    </p>

    <div class="galeria-corpo">
      <p v-if="carregando" class="galeria-aviso" role="status">
        Carregando imagens...
      </p>
      <div v-else-if="erro" class="galeria-aviso" role="alert">
        <p>Não foi possível carregar as imagens. {{ erro }}</p>
        <button
          class="popup-acao popup-acao-cancelar"
          type="button"
          @click="carregar(true)"
        >
          Tentar novamente
        </button>
      </div>
      <p v-else-if="!imagensFiltradas.length" class="galeria-aviso">
        Nenhuma imagem encontrada.
      </p>
      <ul v-else class="galeria-grade">
        <li v-for="item in imagensFiltradas" :key="item.id">
          <button
            class="galeria-item"
            :class="{ 'galeria-item-atual': item.id === imagem?.id }"
            type="button"
            :aria-pressed="item.id === imagem?.id ? 'true' : 'false'"
            @click="escolher(item)"
          >
            <img :src="item.data_uri" alt="" />
            <span :title="item.name ?? item.id">{{
              item.name ?? item.id
            }}</span>
          </button>
        </li>
      </ul>
    </div>
  </PopupTemplate>
</template>

<style scoped>
.seletor {
  display: grid;
  width: 100%;
  height: 100%;
  min-height: 140px;
  overflow: hidden;
  border: 3px dashed #9ba5a0;
  border-radius: 14px;
  background: var(--cor-superficie);
}

.seletor-invalido {
  border-color: #d11a1a;
}

.seletor-vazio {
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 10px;
  border: 0;
  border-radius: 12px;
  color: var(--cor-texto-secundario);
  background: transparent;
  font: 700 1rem var(--fonte);
  cursor: pointer;
}

.seletor-vazio:hover,
.seletor-vazio:focus-visible {
  outline: none;
  background: rgba(0, 142, 21, 0.06);
}

.seletor-vazio svg {
  width: 88px;
  height: 88px;
  stroke-width: 1.5;
}

.seletor-compacto .seletor-vazio svg {
  width: 44px;
  height: 44px;
}

.seletor-compacto .seletor-vazio {
  font-size: 0.85rem;
}

.seletor-previa {
  position: relative;
  display: flex;
  min-height: 0;
  margin: 0;
  /* Espaço no topo para os botões Trocar/Remover não cobrirem a molécula. */
  padding: 44px 10px 10px;
  align-items: center;
  justify-content: center;
}

/* Altura vinda da caixa (não da imagem): SVGs grandes encolhem em vez de vazar. */
.seletor-previa img {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 0;
  object-fit: contain;
}

.seletor-acoes {
  position: absolute;
  top: 6px;
  left: 6px;
  display: flex;
  gap: 6px;
}

.seletor-acoes button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-height: 32px;
  padding: 0 10px;
  border: 2px solid #9ba5a0;
  border-radius: 999px;
  color: var(--cor-texto-secundario);
  background: rgba(255, 255, 255, 0.92);
  font: 700 0.85rem var(--fonte);
  cursor: pointer;
}

.seletor-acoes button:hover,
.seletor-acoes button:focus-visible {
  border-color: var(--cor-principal);
  color: var(--cor-principal);
}

.seletor-acoes svg {
  width: 16px;
  height: 16px;
}

.galeria-topo {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
}

.galeria-importar {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  padding: 0 20px;
  border: 3px solid var(--cor-principal);
  border-radius: 999px;
  color: var(--cor-principal);
  font-weight: 800;
  cursor: pointer;
}

.galeria-importar:focus-within {
  box-shadow: 0 0 0 4px rgba(0, 142, 21, 0.16);
}

.galeria-importar-ocupado {
  opacity: 0.6;
  cursor: wait;
}

.galeria-filtro {
  flex: 1;
  min-width: 200px;
}

.galeria-filtro input {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  border: 3px solid #9ba5a0;
  border-radius: 999px;
  font: 600 1rem var(--fonte);
}

.galeria-filtro input:focus-visible {
  outline: none;
  border-color: var(--cor-principal);
}

.galeria-erro {
  color: #d11a1a !important;
  font-weight: 700;
}

.galeria-corpo {
  flex: 1;
  min-height: 0;
  margin-top: 12px;
  overflow-y: auto;
}

.galeria-aviso {
  display: grid;
  justify-items: center;
  gap: 12px;
  padding: 30px;
  text-align: center;
}

.galeria-grade {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin: 0;
  padding: 4px;
  list-style: none;
}

.galeria-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  width: 100%;
  min-width: 0;
  overflow: hidden;
  gap: 6px;
  padding: 10px;
  border: 3px solid #d3dbd6;
  border-radius: 14px;
  color: var(--cor-texto-secundario);
  background: var(--cor-superficie);
  font: 700 0.9rem var(--fonte);
  cursor: pointer;
}

.galeria-item img {
  display: block;
  width: 100%;
  height: 90px;
  object-fit: contain;
}

/* Nomes longos (ex.: importados de pacotes) terminam em "..."; o nome inteiro fica no title. */
.galeria-item span {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.galeria-item:hover,
.galeria-item:focus-visible {
  outline: none;
  border-color: var(--cor-principal);
}

.galeria-item-atual {
  border-color: var(--cor-principal);
  background: rgba(0, 142, 21, 0.06);
}
</style>
