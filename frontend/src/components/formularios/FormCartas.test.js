import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { reactive } from "vue";
import FormAssociacao from "./FormAssociacao.vue";
import FormMoleculaDaFuncao from "./FormMoleculaDaFuncao.vue";
import * as associacao from "./associacao";
import * as moleculaDaFuncao from "./moleculaDaFuncao";

function montar(componente, logica) {
  const rascunho = reactive(logica.criarRascunho());
  const wrapper = mount(componente, { props: { rascunho, erros: {} } });
  return { wrapper, rascunho };
}

describe("formulários de cartas", () => {
  it("associação: no máximo duas cartas e a terceira fica bloqueada", async () => {
    const { wrapper, rascunho } = montar(FormAssociacao, associacao);
    const marcadores = wrapper.findAll(".marcador");
    expect(wrapper.findAll(".carta")).toHaveLength(4);

    await marcadores[0].trigger("click");
    await marcadores[2].trigger("click");
    expect(rascunho.par).toEqual(["C1", "C3"]);
    expect(marcadores[1].attributes("disabled")).toBeDefined();

    await marcadores[1].trigger("click");
    expect(rascunho.par).toEqual(["C1", "C3"]);

    await marcadores[0].trigger("click");
    expect(rascunho.par).toEqual(["C3"]);
    expect(marcadores[1].attributes("disabled")).toBeUndefined();
  });

  it("qual molécula: só uma carta correta", async () => {
    const { wrapper, rascunho } = montar(
      FormMoleculaDaFuncao,
      moleculaDaFuncao,
    );
    const marcadores = wrapper.findAll(".marcador");

    await marcadores[0].trigger("click");
    await marcadores[3].trigger("click");
    expect(rascunho.correta).toBe("C4");
    expect(marcadores[0].attributes("aria-pressed")).toBe("false");
    expect(marcadores[1].attributes("disabled")).toBeUndefined();
  });

  it("a carta troca entre imagem e texto e mantém o complemento opcional", async () => {
    const { wrapper, rascunho } = montar(FormAssociacao, associacao);
    const primeira = wrapper.findAll(".carta")[0];
    expect(primeira.find(".seletor").exists()).toBe(true);

    await primeira.findAll(".carta-tipo button")[1].trigger("click");
    expect(rascunho.cartas[0].tipo).toBe("texto");
    expect(primeira.find(".carta-texto").exists()).toBe(true);
    expect(primeira.find(".seletor").exists()).toBe(false);
    expect(primeira.find(".carta-complemento").exists()).toBe(true);
  });
});
