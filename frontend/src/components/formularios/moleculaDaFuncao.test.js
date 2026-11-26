import { describe, expect, it } from "vitest";
import {
  criarRascunho,
  deQuestao,
  paraPayload,
  validar,
} from "./moleculaDaFuncao";

describe("formulário de qual molécula pertence à função", () => {
  it("exige uma carta correta", () => {
    const rascunho = criarRascunho();
    expect(validar(rascunho)["payload.correct_card_id"]).toBe(
      "Marque a carta correta.",
    );
  });

  it("monta o payload com uma única carta correta", () => {
    const rascunho = criarRascunho();
    rascunho.enunciado = "Qual molécula pertence à função amina?";
    ["etanol", "propanona", "metilamina", "etanal"].forEach((id, i) => {
      rascunho.cartas[i].imagem = { id };
    });
    rascunho.correta = "C3";
    expect(validar(rascunho)).toEqual({});
    expect(paraPayload(rascunho)).toEqual({
      cards: [
        { id: "C1", asset_id: "etanol" },
        { id: "C2", asset_id: "propanona" },
        { id: "C3", asset_id: "metilamina" },
        { id: "C4", asset_id: "etanal" },
      ],
      correct_card_id: "C3",
    });
  });

  it("preserva o target_function de questões antigas na edição", () => {
    const payload = {
      cards: [
        { id: "C1", content: "Etanol" },
        { id: "C2", content: "Propanona" },
        { id: "C3", content: "Metilamina" },
        { id: "C4", content: "Etanal" },
      ],
      correct_card_id: "C3",
      target_function: "Amina",
    };
    const rascunho = deQuestao({ statement: "Qual?", payload, assets: {} });
    expect(paraPayload(rascunho)).toEqual(payload);
  });
});
