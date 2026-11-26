import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { reactive } from "vue";
import FormOrdemFuncoes from "./FormOrdemFuncoes.vue";
import { criarRascunho } from "./ordemFuncoes";

function montar() {
  const rascunho = reactive(criarRascunho());
  const wrapper = mount(FormOrdemFuncoes, { props: { rascunho, erros: {} } });
  return { wrapper, rascunho };
}

const numeros = (wrapper) =>
  wrapper
    .findAll(".marcador")
    .map((m) => (m.find(".marcador-numero").exists() ? m.text() : null));

describe("FormOrdemFuncoes", () => {
  it("caixas só de imagem, sem texto nem complemento", () => {
    const { wrapper } = montar();
    expect(wrapper.findAll(".carta")).toHaveLength(4);
    expect(wrapper.findAll(".seletor")).toHaveLength(4);
    expect(wrapper.find(".carta-tipo").exists()).toBe(false);
    expect(wrapper.find(".carta-complemento").exists()).toBe(false);
  });

  it("numera na ordem dos cliques e renumera ao desmarcar (exemplo A)", async () => {
    const { wrapper, rascunho } = montar();
    const marcadores = wrapper.findAll(".marcador");
    for (const i of [0, 1, 2, 3]) await marcadores[i].trigger("click");
    expect(numeros(wrapper)).toEqual(["1", "2", "3", "4"]);

    await marcadores[0].trigger("click");
    expect(rascunho.ordem).toEqual(["M2", "M3", "M4"]);
    expect(numeros(wrapper)).toEqual([null, "1", "2", "3"]);

    await marcadores[0].trigger("click");
    expect(numeros(wrapper)).toEqual(["4", "1", "2", "3"]);
  });

  it("desmarcar a 3ª de três não mexe nas anteriores (exemplo B)", async () => {
    const { wrapper, rascunho } = montar();
    const marcadores = wrapper.findAll(".marcador");
    for (const i of [0, 1, 2]) await marcadores[i].trigger("click");
    await marcadores[2].trigger("click");
    expect(rascunho.ordem).toEqual(["M1", "M2"]);
    expect(numeros(wrapper)).toEqual(["1", "2", null, null]);
  });
});
