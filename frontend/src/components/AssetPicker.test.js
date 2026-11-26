import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../services/questoes", () => ({
  listarAssets: vi.fn(),
  importarSvg: vi.fn(),
}));

import { importarSvg, listarAssets } from "../services/questoes";
import { useBibliotecaImagens } from "../composables/useBibliotecaImagens";
import AssetPicker from "./AssetPicker.vue";

const SVG =
  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4=";
const etanol = {
  id: "etanol",
  name: "Etanol",
  data_uri: SVG,
  region_ids: ["grupo-oh"],
};
const propanona = {
  id: "propanona",
  name: "Propanona",
  data_uri: SVG,
  region_ids: [],
};

function montar(modelValue = null) {
  return mount(AssetPicker, {
    attachTo: document.body,
    props: {
      modelValue,
      "onUpdate:modelValue": (valor) => wrapper.setProps({ modelValue: valor }),
    },
  });
}

let wrapper;

// O jsdom não implementa File.text(); o componente só usa name e text().
function arquivoFalso(name, conteudo) {
  return { name, text: async () => conteudo };
}

describe("AssetPicker", () => {
  beforeEach(() => {
    useBibliotecaImagens().reiniciar();
    listarAssets.mockReset().mockResolvedValue([etanol, propanona]);
    importarSvg.mockReset();
  });

  afterEach(() => {
    wrapper?.unmount();
    document.body.innerHTML = "";
  });

  it("abre a galeria e escolhe uma imagem existente", async () => {
    wrapper = montar();
    await wrapper.find(".seletor-vazio").trigger("click");
    await flushPromises();

    expect(listarAssets).toHaveBeenCalledWith(undefined, true);
    [...document.querySelectorAll(".galeria-item")]
      .find((b) => b.textContent.includes("Propanona"))
      .click();
    await flushPromises();

    expect(wrapper.emitted("update:modelValue").at(-1)).toEqual([propanona]);
    expect(document.body.textContent).not.toContain("Selecionar imagem");
    expect(wrapper.find(".seletor-previa img").exists()).toBe(true);
  });

  it("filtra a galeria pelo nome", async () => {
    wrapper = montar();
    await wrapper.find(".seletor-vazio").trigger("click");
    await flushPromises();

    const filtro = document.querySelector(".galeria-filtro input");
    filtro.value = "eta";
    filtro.dispatchEvent(new Event("input"));
    await flushPromises();

    const nomes = [...document.querySelectorAll(".galeria-item")].map((b) =>
      b.textContent.trim(),
    );
    expect(nomes).toEqual(["Etanol"]);
  });

  it("importa um arquivo SVG e seleciona o resultado", async () => {
    const nova = { id: "nova", name: "Ácido", data_uri: SVG, region_ids: [] };
    importarSvg.mockResolvedValue(nova);
    wrapper = montar();
    await wrapper.find(".seletor-vazio").trigger("click");
    await flushPromises();

    const input = document.querySelector(".galeria-importar input");
    Object.defineProperty(input, "files", {
      value: [
        arquivoFalso("Ácido.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>'),
      ],
    });
    input.dispatchEvent(new Event("change"));
    await flushPromises();

    expect(importarSvg).toHaveBeenCalledWith(
      '<svg xmlns="http://www.w3.org/2000/svg"/>',
      "Ácido",
    );
    expect(wrapper.emitted("update:modelValue").at(-1)).toEqual([nova]);
  });

  it("mostra o erro de importação sem perder a seleção atual", async () => {
    importarSvg.mockRejectedValue({
      message: "Dados inválidos",
      detalhes: [{ campo: "conteudo", mensagem: "SVG contém <script>" }],
    });
    wrapper = montar(etanol);
    await wrapper.find(".seletor-acoes button").trigger("click");
    await flushPromises();

    const input = document.querySelector(".galeria-importar input");
    Object.defineProperty(input, "files", {
      value: [arquivoFalso("ruim.svg", "x")],
    });
    input.dispatchEvent(new Event("change"));
    await flushPromises();

    expect(document.body.textContent).toContain("SVG contém <script>");
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
  });

  it("remover limpa a seleção", async () => {
    wrapper = montar(etanol);
    await wrapper.findAll(".seletor-acoes button")[1].trigger("click");
    expect(wrapper.emitted("update:modelValue").at(-1)).toEqual([null]);
  });
});
