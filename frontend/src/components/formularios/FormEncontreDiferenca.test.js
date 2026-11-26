import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { reactive } from "vue";
import FormEncontreDiferenca from "./FormEncontreDiferenca.vue";
import { criarRascunho } from "./encontreDiferenca";

function montar(erros = {}) {
  // No modal o rascunho é reativo (ref); aqui também, para a tela acompanhar as mudanças.
  const rascunho = reactive(criarRascunho());
  const wrapper = mount(FormEncontreDiferenca, { props: { rascunho, erros } });
  return { wrapper, rascunho };
}

describe("FormEncontreDiferenca", () => {
  it("tem duas caixas de imagem", () => {
    const { wrapper } = montar();
    expect(wrapper.findAll(".seletor")).toHaveLength(2);
  });

  it("só uma caixa fica marcada como correta", async () => {
    const { wrapper, rascunho } = montar();
    const [primeira, segunda] = wrapper.findAll(".marcador");

    await primeira.trigger("click");
    expect(rascunho.correta).toBe("M1");

    await segunda.trigger("click");
    expect(rascunho.correta).toBe("M2");
    expect(primeira.attributes("aria-pressed")).toBe("false");
    expect(segunda.attributes("aria-pressed")).toBe("true");

    await segunda.trigger("click");
    expect(rascunho.correta).toBeNull();
  });

  it("mostra o erro da imagem faltando na caixa certa", () => {
    const { wrapper } = montar({
      "payload.molecules.1.asset_id": "Escolha a imagem.",
    });
    const caixas = wrapper.findAll(".form-caixa-bloco");
    expect(caixas[0].text()).not.toContain("Escolha a imagem.");
    expect(caixas[1].text()).toContain("Escolha a imagem.");
    expect(caixas[1].find(".seletor").classes()).toContain("seletor-invalido");
  });
});
