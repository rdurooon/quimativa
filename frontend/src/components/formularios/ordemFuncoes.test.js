import { describe, expect, it } from "vitest";
import { criarRascunho, deQuestao, paraPayload, validar } from "./ordemFuncoes";

describe("formulário de ordem das funções", () => {
  it("exige as quatro imagens e a sequência completa", () => {
    const rascunho = criarRascunho();
    rascunho.ordem = ["M1", "M2", "M3"];
    expect(validar(rascunho)).toEqual({
      statement: "Escreva o enunciado.",
      "payload.molecules.0": "Escolha a imagem.",
      "payload.molecules.1": "Escolha a imagem.",
      "payload.molecules.2": "Escolha a imagem.",
      "payload.molecules.3": "Escolha a imagem.",
      "payload.correct_order": "Numere as quatro moléculas na ordem correta.",
    });
  });

  it("monta o payload do contrato e volta igual na edição", () => {
    const rascunho = criarRascunho();
    rascunho.enunciado = "Ordene: Álcool, Éster, Amida, Amina.";
    ["alcool", "amina", "amida", "ester"].forEach((id, i) => {
      rascunho.cartas[i].imagem = { id };
    });
    rascunho.ordem = ["M1", "M4", "M3", "M2"];
    expect(validar(rascunho)).toEqual({});

    const payload = paraPayload(rascunho);
    expect(payload).toEqual({
      molecules: [
        { id: "M1", asset_id: "alcool" },
        { id: "M2", asset_id: "amina" },
        { id: "M3", asset_id: "amida" },
        { id: "M4", asset_id: "ester" },
      ],
      correct_order: ["M1", "M4", "M3", "M2"],
    });

    const assets = Object.fromEntries(
      ["alcool", "amina", "amida", "ester"].map((id) => [id, { id }]),
    );
    expect(
      paraPayload(deQuestao({ statement: "Ordene.", payload, assets })),
    ).toEqual(payload);
  });
});
