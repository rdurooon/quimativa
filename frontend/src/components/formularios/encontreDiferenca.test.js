import { describe, expect, it } from "vitest";
import {
  criarRascunho,
  deQuestao,
  paraPayload,
  validar,
} from "./encontreDiferenca";

function preenchido() {
  const rascunho = criarRascunho();
  rascunho.enunciado = "Qual molécula é um álcool?";
  rascunho.moleculas[0].imagem = { id: "etanol" };
  rascunho.moleculas[1].imagem = { id: "propanona" };
  rascunho.correta = "M1";
  return rascunho;
}

describe("formulário de encontre a diferença", () => {
  it("rascunho novo tem duas caixas vazias", () => {
    expect(criarRascunho().moleculas).toEqual([
      { id: "M1", imagem: null },
      { id: "M2", imagem: null },
    ]);
  });

  it("aponta enunciado, imagens e resposta faltando", () => {
    expect(Object.keys(validar(criarRascunho())).sort()).toEqual([
      "payload.correct_molecule_id",
      "payload.molecules.0.asset_id",
      "payload.molecules.1.asset_id",
      "statement",
    ]);
  });

  it("monta o payload sem criterion em questão nova", () => {
    expect(paraPayload(preenchido())).toEqual({
      molecules: [
        { id: "M1", asset_id: "etanol" },
        { id: "M2", asset_id: "propanona" },
      ],
      correct_molecule_id: "M1",
    });
  });

  it("preserva o criterion de uma questão antiga na edição", () => {
    const questao = {
      statement: "Qual é o álcool?",
      payload: {
        molecules: [
          { id: "M1", asset_id: "etanol" },
          { id: "M2", asset_id: "propanona" },
        ],
        criterion: "Possui hidroxila",
        correct_molecule_id: "M2",
      },
      assets: { etanol: { id: "etanol" }, propanona: { id: "propanona" } },
    };
    const rascunho = deQuestao(questao);
    expect(rascunho.correta).toBe("M2");
    expect(paraPayload(rascunho)).toEqual(questao.payload);
  });
});
