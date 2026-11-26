// Associação de cartas: quatro cartas e exatamente duas formam o par correto.
import {
  cartaDeQuestao,
  cartaParaPayload,
  criarCartas,
  validarCartas,
} from "./cartas";

export function criarRascunho() {
  return { enunciado: "", cartas: criarCartas(), par: [] };
}

export function validar(rascunho) {
  const erros = {};
  if (!rascunho.enunciado.trim()) erros.statement = "Escreva o enunciado.";
  validarCartas(rascunho.cartas, erros);
  if (rascunho.par.length !== 2)
    erros["payload.correct_pair"] = "Marque as duas cartas do par correto.";
  return erros;
}

export function paraPayload(rascunho) {
  return {
    cards: rascunho.cartas.map(cartaParaPayload),
    correct_pair: [...rascunho.par],
  };
}

export function deQuestao(questao) {
  return {
    enunciado: questao.statement,
    cartas: questao.payload.cards.map((carta) =>
      cartaDeQuestao(carta, questao.assets),
    ),
    par: [...questao.payload.correct_pair],
  };
}
