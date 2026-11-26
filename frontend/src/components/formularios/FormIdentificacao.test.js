import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { nextTick, ref } from "vue";
import FormIdentificacao from "./FormIdentificacao.vue";
import { criarRascunho } from "./identificacao";

const SVG =
  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4=";

function montar(rascunho = criarRascunho(), erros = {}) {
  const modelo = ref(rascunho);
  const wrapper = mount(FormIdentificacao, {
    props: {
      rascunho: modelo.value,
      "onUpdate:rascunho": (valor) => {
        modelo.value = valor;
      },
      erros,
    },
  });
  return { wrapper, modelo };
}

describe("FormIdentificacao", () => {
  it("marca a alternativa correta pelo círculo", async () => {
    const { wrapper, modelo } = montar();
    await wrapper.findAll('input[type="radio"]')[2].setValue(true);
    expect(modelo.value.correta).toBe("C");
    expect(wrapper.findAll(".form-alternativa")[2].classes()).toContain(
      "form-alternativa-correta",
    );
  });

  it("escolhe sozinha a região quando a imagem tem uma só", async () => {
    const { wrapper, modelo } = montar();
    modelo.value.imagem = {
      id: "etanol",
      data_uri: SVG,
      region_ids: ["grupo-oh"],
    };
    await nextTick();
    await nextTick();
    expect(modelo.value.regiao).toBe("grupo-oh");
    expect(wrapper.find(".form-regiao select").exists()).toBe(true);
  });

  it("avisa quando a imagem não tem regiões", async () => {
    const { wrapper, modelo } = montar();
    modelo.value.imagem = { id: "x", data_uri: SVG, region_ids: [] };
    await nextTick();
    expect(wrapper.text()).toContain("Esta imagem não tem regiões marcadas");
  });

  it("mostra os erros de cada campo", () => {
    const { wrapper } = montar(criarRascunho(), {
      statement: "Escreva o enunciado.",
      "payload.alternatives.1.label": "Preencha a alternativa.",
    });
    expect(wrapper.text()).toContain("Escreva o enunciado.");
    expect(wrapper.findAll(".form-alternativa")[1].classes()).toContain(
      "form-campo-invalido",
    );
  });
});
