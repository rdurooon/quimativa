import { describe, expect, it } from "vitest";
import {
  criarRascunho,
  deQuestao,
  paraPayload,
  validar,
} from "./identificacao";

function preenchido() {
  const rascunho = criarRascunho();
  rascunho.enunciado = "  Qual função está destacada?  ";
  rascunho.imagem = { id: "etanol", region_ids: ["grupo-oh"] };
  rascunho.regiao = "grupo-oh";
  ["Álcool", "Cetona", "Éster", " Aldeído "].forEach((texto, i) => {
    rascunho.alternativas[i].label = texto;
  });
  rascunho.correta = "A";
  return rascunho;
}

describe("formulário de identificação", () => {
  it("rascunho novo tem 4 alternativas vazias e nenhuma correta", () => {
    const rascunho = criarRascunho();
    expect(rascunho.alternativas.map((a) => a.id)).toEqual([
      "A",
      "B",
      "C",
      "D",
    ]);
    expect(rascunho.correta).toBeNull();
  });

  it("aponta cada campo faltando com a chave usada pelo backend", () => {
    expect(Object.keys(validar(criarRascunho())).sort()).toEqual([
      "payload.alternatives.0.label",
      "payload.alternatives.1.label",
      "payload.alternatives.2.label",
      "payload.alternatives.3.label",
      "payload.correct_alternative_id",
      "payload.molecule_asset_id",
      "statement",
    ]);
  });

  it("pede a região quando a imagem já foi escolhida", () => {
    const rascunho = preenchido();
    rascunho.regiao = "";
    expect(validar(rascunho)).toEqual({
      "payload.highlight.region_id": "Escolha a região destacada.",
    });
  });

  it("monta o payload do contrato", () => {
    const rascunho = preenchido();
    expect(validar(rascunho)).toEqual({});
    expect(paraPayload(rascunho)).toEqual({
      molecule_asset_id: "etanol",
      highlight: { region_id: "grupo-oh" },
      alternatives: [
        { id: "A", label: "Álcool" },
        { id: "B", label: "Cetona" },
        { id: "C", label: "Éster" },
        { id: "D", label: "Aldeído" },
      ],
      correct_alternative_id: "A",
    });
  });

  it("reconstrói o rascunho a partir da questão salva", () => {
    const imagem = {
      id: "etanol",
      region_ids: ["grupo-oh"],
      data_uri: "data:...",
    };
    const questao = {
      statement: "Qual função?",
      payload: paraPayload(preenchido()),
      assets: { etanol: imagem },
    };
    const rascunho = deQuestao(questao);
    expect(rascunho.imagem).toBe(imagem);
    expect(rascunho.regiao).toBe("grupo-oh");
    expect(rascunho.correta).toBe("A");
    expect(paraPayload(rascunho)).toEqual(questao.payload);
  });
});
