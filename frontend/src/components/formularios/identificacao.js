// Identificação de função orgânica e Análise molecular usam o mesmo formato de payload.
// As chaves de erro seguem os campos do backend, então erros locais e da bridge caem no mesmo lugar.

export const LETRAS = ["A", "B", "C", "D"];

export function criarRascunho() {
  return {
    enunciado: "",
    imagem: null,
    regiao: "",
    alternativas: LETRAS.map((id) => ({ id, label: "" })),
    correta: null,
  };
}

export function validar(rascunho) {
  const erros = {};
  if (!rascunho.enunciado.trim()) erros.statement = "Escreva o enunciado.";
  if (!rascunho.imagem) {
    erros["payload.molecule_asset_id"] = "Escolha a imagem da molécula.";
  } else if (!rascunho.regiao) {
    erros["payload.highlight.region_id"] = "Escolha a região destacada.";
  }
  rascunho.alternativas.forEach((alternativa, indice) => {
    if (!alternativa.label.trim())
      erros[`payload.alternatives.${indice}.label`] = "Preencha a alternativa.";
  });
  if (!rascunho.correta)
    erros["payload.correct_alternative_id"] = "Marque a alternativa correta.";
  return erros;
}

export function paraPayload(rascunho) {
  return {
    molecule_asset_id: rascunho.imagem.id,
    highlight: { region_id: rascunho.regiao },
    alternatives: rascunho.alternativas.map(({ id, label }) => ({
      id,
      label: label.trim(),
    })),
    correct_alternative_id: rascunho.correta,
  };
}

/** Rascunho a partir de uma questão completa (questoes_obter), para a edição. */
export function deQuestao(questao) {
  const payload = questao.payload;
  return {
    enunciado: questao.statement,
    imagem: questao.assets?.[payload.molecule_asset_id] ?? null,
    regiao: payload.highlight?.region_id ?? "",
    alternativas: payload.alternatives.map(({ id, label }) => ({ id, label })),
    correta: payload.correct_alternative_id,
  };
}
