import { ref } from "vue";
import { importarSvg, listarAssets } from "../services/questoes";

// Estado compartilhado: os 4 seletores de um formulário usam a mesma lista e ela é carregada uma vez.
const imagens = ref([]);
const carregando = ref(false);
const erro = ref("");
let carregada = false;

async function carregar(forcar = false) {
  if ((carregada && !forcar) || carregando.value) return;
  carregando.value = true;
  erro.value = "";
  try {
    imagens.value = await listarAssets(undefined, true);
    carregada = true;
  } catch (falha) {
    erro.value = falha.message;
  } finally {
    carregando.value = false;
  }
}

/** Importa o arquivo .svg e devolve a imagem; o backend reaproveita um SVG idêntico já existente. */
async function importar(arquivo) {
  const nome = arquivo.name.replace(/\.svg$/i, "");
  const imagem = await importarSvg(await arquivo.text(), nome);
  if (!imagens.value.some((item) => item.id === imagem.id)) {
    imagens.value = [...imagens.value, imagem];
  }
  return imagem;
}

function reiniciar() {
  imagens.value = [];
  erro.value = "";
  carregada = false;
}

export function useBibliotecaImagens() {
  return { imagens, carregando, erro, carregar, importar, reiniciar };
}
