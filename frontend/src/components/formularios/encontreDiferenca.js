// Encontre a diferença: duas moléculas e exatamente uma correta.
// O enunciado (statement) é o critério; criterion só existe em payloads antigos e é preservado na edição.

const IDS = ["M1", "M2"];

export function criarRascunho() {
  return {
    enunciado: "",
    moleculas: IDS.map((id) => ({ id, imagem: null })),
    correta: null,
    criterio: null,
  };
}

export function validar(rascunho) {
  const erros = {};
  if (!rascunho.enunciado.trim()) erros.statement = "Escreva o enunciado.";
  rascunho.moleculas.forEach((molecula, indice) => {
    if (!molecula.imagem)
      erros[`payload.molecules.${indice}.asset_id`] = "Escolha a imagem.";
  });
  if (!rascunho.correta)
    erros["payload.correct_molecule_id"] = "Marque a molécula correta.";
  return erros;
}

export function paraPayload(rascunho) {
  const payload = {
    molecules: rascunho.moleculas.map(({ id, imagem }) => ({
      id,
      asset_id: imagem.id,
    })),
    correct_molecule_id: rascunho.correta,
  };
  if (rascunho.criterio) payload.criterion = rascunho.criterio;
  return payload;
}

export function deQuestao(questao) {
  const payload = questao.payload;
  return {
    enunciado: questao.statement,
    moleculas: payload.molecules.map(({ id, asset_id: assetId }) => ({
      id,
      imagem: questao.assets?.[assetId] ?? null,
    })),
    correta: payload.correct_molecule_id,
    criterio: payload.criterion ?? null,
  };
}
