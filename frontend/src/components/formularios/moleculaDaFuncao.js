// Qual molécula pertence à função?: quatro cartas e exatamente uma correta.
// A função procurada vai no enunciado; target_function só existe em questões antigas e é preservado.
import {
  cartaDeQuestao,
  cartaParaPayload,
  criarCartas,
  validarCartas,
} from "./cartas";

export function criarRascunho() {
  return {
    enunciado: "",
    cartas: criarCartas(),
    correta: null,
    funcaoAntiga: null,
  };
}

export function validar(rascunho) {
  const erros = {};
  if (!rascunho.enunciado.trim()) erros.statement = "Escreva o enunciado.";
  validarCartas(rascunho.cartas, erros);
  if (!rascunho.correta)
    erros["payload.correct_card_id"] = "Marque a carta correta.";
  return erros;
}

export function paraPayload(rascunho) {
  const payload = {
    cards: rascunho.cartas.map(cartaParaPayload),
    correct_card_id: rascunho.correta,
  };
  if (rascunho.funcaoAntiga) payload.target_function = rascunho.funcaoAntiga;
  return payload;
}

export function deQuestao(questao) {
  return {
    enunciado: questao.statement,
    cartas: questao.payload.cards.map((carta) =>
      cartaDeQuestao(carta, questao.assets),
    ),
    correta: questao.payload.correct_card_id,
    funcaoAntiga: questao.payload.target_function ?? null,
  };
}
