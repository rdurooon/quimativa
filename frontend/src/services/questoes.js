import { callDesktop } from "./desktop";

export class ErroBridge extends Error {
  constructor(erro) {
    super(erro?.mensagem ?? "Não foi possível concluir a operação.");
    this.name = "ErroBridge";
    this.codigo = erro?.codigo ?? "erro_interno";
    this.detalhes = Array.isArray(erro?.detalhes) ? erro.detalhes : [];
  }
}

export function errosPorCampo(erro) {
  const mapa = {};
  for (const { campo, mensagem } of erro?.detalhes ?? []) {
    if (campo && !(campo in mapa)) mapa[campo] = mensagem;
  }
  return mapa;
}

async function chamar(metodo, ...args) {
  let resposta;
  try {
    resposta = await callDesktop(metodo, ...args);
  } catch (falha) {
    throw new ErroBridge({
      codigo: "bridge_indisponivel",
      mensagem: falha.message,
    });
  }
  if (!resposta?.ok) throw new ErroBridge(resposta?.erro);
  return resposta.dados;
}

export const obterMetadados = () => chamar("questoes_metadados");
export const listarQuestoes = (filtros) => chamar("questoes_listar", filtros);
export const obterQuestao = (id) => chamar("questoes_obter", id);
export const criarQuestao = (dados) => chamar("questoes_criar", dados);
export const atualizarQuestao = (id, dados) =>
  chamar("questoes_atualizar", id, dados);
export const removerQuestao = (id) => chamar("questoes_remover", id);

export const listarPacotes = () => chamar("pacotes_listar");
export const criarPacote = (nome) => chamar("pacotes_criar", { name: nome });
export const removerPacote = (id) => chamar("pacotes_remover", id);

export const importarSvg = (conteudo, nome) =>
  chamar("assets_importar_svg", conteudo, nome);
export const listarAssets = (origem, comConteudo = false) =>
  chamar("assets_listar", origem, comConteudo);
export const obterAsset = (id) => chamar("assets_obter", id);
export const removerAsset = (id) => chamar("assets_remover", id);
