import { describe, expect, it } from "vitest";
import { FORMULARIOS } from "./registro";
import FormIdentificacao from "./FormIdentificacao.vue";
import FormEncontreDiferenca from "./FormEncontreDiferenca.vue";
import FormAssociacao from "./FormAssociacao.vue";
import FormMoleculaDaFuncao from "./FormMoleculaDaFuncao.vue";
import FormOrdemFuncoes from "./FormOrdemFuncoes.vue";

describe("registro de formulários", () => {
  it("cada minigame aponta para o formulário certo", () => {
    expect(FORMULARIOS.identification.componente).toBe(FormIdentificacao);
    expect(FORMULARIOS.molecular_analysis.componente).toBe(FormIdentificacao);
    expect(FORMULARIOS.find_difference.componente).toBe(FormEncontreDiferenca);
    expect(FORMULARIOS.card_association.componente).toBe(FormAssociacao);
    expect(FORMULARIOS.function_molecule.componente).toBe(FormMoleculaDaFuncao);
    expect(FORMULARIOS.function_order.componente).toBe(FormOrdemFuncoes);
  });

  it("todo formulário registrado tem as quatro funções", () => {
    for (const [tipo, formulario] of Object.entries(FORMULARIOS)) {
      for (const funcao of [
        "criarRascunho",
        "validar",
        "paraPayload",
        "deQuestao",
      ]) {
        expect(typeof formulario[funcao], `${tipo}.${funcao}`).toBe("function");
      }
    }
  });
});
