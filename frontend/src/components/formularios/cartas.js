// Peças comuns às cartas da grade 2×2 (Associação de cartas e Qual molécula pertence à função).
// Cada carta é imagem OU texto principal, com texto complementar opcional.

export const IDS_CARTAS = ["C1", "C2", "C3", "C4"];

export function criarCartas() {
  return IDS_CARTAS.map((id) => ({
    id,
    tipo: "imagem",
    imagem: null,
    texto: "",
    complemento: "",
  }));
}

export function validarCartas(cartas, erros) {
  cartas.forEach((carta, indice) => {
    if (carta.tipo === "imagem" && !carta.imagem) {
      erros[`payload.cards.${indice}`] = "Escolha a imagem da carta.";
    } else if (carta.tipo === "texto" && !carta.texto.trim()) {
      erros[`payload.cards.${indice}`] = "Escreva o texto da carta.";
    }
  });
}

export function cartaParaPayload(carta) {
  const resultado = { id: carta.id };
  if (carta.tipo === "imagem") resultado.asset_id = carta.imagem.id;
  else resultado.content = carta.texto.trim();
  const complemento = carta.complemento.trim();
  if (complemento) resultado.supplementary_text = complemento;
  return resultado;
}

export function cartaDeQuestao(carta, assets) {
  return {
    id: carta.id,
    tipo: carta.asset_id ? "imagem" : "texto",
    imagem: carta.asset_id ? (assets?.[carta.asset_id] ?? null) : null,
    texto: carta.content ?? "",
    complemento: carta.supplementary_text ?? "",
  };
}
