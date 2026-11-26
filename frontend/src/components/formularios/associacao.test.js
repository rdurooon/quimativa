import { describe, expect, it } from "vitest";
import { criarRascunho, deQuestao, paraPayload, validar } from "./associacao";

function preenchido() {
  const rascunho = criarRascunho();
  rascunho.enunciado = "Associe a molécula à sua função.";
  rascunho.cartas[0].imagem = { id: "etanol" };
  rascunho.cartas[1].tipo = "texto";
  rascunho.cartas[1].texto = " Álcool ";
  rascunho.cartas[1].complemento = "grupo OH";
  rascunho.cartas[2].imagem = { id: "propanona" };
  rascunho.cartas[3].tipo = "texto";
  rascunho.cartas[3].texto = "Cetona";
  rascunho.par = ["C1", "C2"];
  return rascunho;
}

describe("formulário de associação de cartas", () => {
  it("rascunho novo tem quatro cartas de imagem e nenhum par", () => {
    const rascunho = criarRascunho();
    expect(rascunho.cartas.map((c) => [c.id, c.tipo])).toEqual([
      ["C1", "imagem"],
      ["C2", "imagem"],
      ["C3", "imagem"],
      ["C4", "imagem"],
    ]);
    expect(rascunho.par).toEqual([]);
  });

  it("aponta carta sem imagem, carta de texto vazia e par incompleto", () => {
    const rascunho = criarRascunho();
    rascunho.cartas[1].tipo = "texto";
    rascunho.par = ["C1"];
    expect(validar(rascunho)).toEqual({
      statement: "Escreva o enunciado.",
      "payload.cards.0": "Escolha a imagem da carta.",
      "payload.cards.1": "Escreva o texto da carta.",
      "payload.cards.2": "Escolha a imagem da carta.",
      "payload.cards.3": "Escolha a imagem da carta.",
      "payload.correct_pair": "Marque as duas cartas do par correto.",
    });
  });

  it("cada carta vai com imagem ou texto, nunca os dois, e complemento só se preenchido", () => {
    const rascunho = preenchido();
    rascunho.cartas[0].texto = "sobra de quando era texto";
    expect(validar(rascunho)).toEqual({});
    expect(paraPayload(rascunho)).toEqual({
      cards: [
        { id: "C1", asset_id: "etanol" },
        { id: "C2", content: "Álcool", supplementary_text: "grupo OH" },
        { id: "C3", asset_id: "propanona" },
        { id: "C4", content: "Cetona" },
      ],
      correct_pair: ["C1", "C2"],
    });
  });

  it("reconstrói o rascunho da questão salva", () => {
    const payload = paraPayload(preenchido());
    const assets = { etanol: { id: "etanol" }, propanona: { id: "propanona" } };
    const rascunho = deQuestao({ statement: "Associe.", payload, assets });
    expect(rascunho.cartas[1].tipo).toBe("texto");
    expect(paraPayload(rascunho)).toEqual(payload);
  });
});
