// Ordem das funções: quatro moléculas (só imagem) e a sequência correta entre elas.
// A sequência guarda os IDs na ordem em que foram marcados; o número de cada caixa sai da posição nela.

const IDS = ["M1", "M2", "M3", "M4"];

export function criarRascunho() {
  return {
    enunciado: "",
    cartas: IDS.map((id) => ({
      id,
      tipo: "imagem",
      imagem: null,
      texto: "",
      complemento: "",
    })),
    ordem: [],
  };
}

export function validar(rascunho) {
  const erros = {};
  if (!rascunho.enunciado.trim()) erros.statement = "Escreva o enunciado.";
  rascunho.cartas.forEach((carta, indice) => {
    if (!carta.imagem)
      erros[`payload.molecules.${indice}`] = "Escolha a imagem.";
  });
  if (rascunho.ordem.length !== IDS.length) {
    erros["payload.correct_order"] =
      "Numere as quatro moléculas na ordem correta.";
  }
  return erros;
}

export function paraPayload(rascunho) {
  return {
    molecules: rascunho.cartas.map(({ id, imagem }) => ({
      id,
      asset_id: imagem.id,
    })),
    correct_order: [...rascunho.ordem],
  };
}

export function deQuestao(questao) {
  const payload = questao.payload;
  return {
    enunciado: questao.statement,
    cartas: payload.molecules.map(({ id, asset_id: assetId }) => ({
      id,
      tipo: "imagem",
      imagem: questao.assets?.[assetId] ?? null,
      texto: "",
      complemento: "",
    })),
    ordem: [...payload.correct_order],
  };
}
