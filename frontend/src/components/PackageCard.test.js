import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import PackageCard from "./PackageCard.vue";

const minigames = [
  { value: "identification", name: "Identificação de função orgânica" },
  { value: "find_difference", name: "Encontre a diferença" },
];
const difficulties = [
  { value: 1, name: "Fácil" },
  { value: 2, name: "Média" },
  { value: 3, name: "Difícil" },
];

function montar(pacote) {
  return mount(PackageCard, { props: { pacote, minigames, difficulties } });
}

describe("PackageCard", () => {
  it('pacote base mostra "Já instalado" e não oferece remover', () => {
    const card = montar({
      id: "base",
      name: "Questões-base",
      kind: "base",
      question_count: 6,
      minigame_types: ["identification", "find_difference"],
      difficulties: [1, 2, 3],
      permissions: { delete: false },
    });
    expect(card.text()).toContain("Já instalado");
    expect(card.find(".pacote-remover").exists()).toBe(false);
    expect(card.text()).toContain("Encontre a diferença");
    expect(card.findAll(".chip-dificuldade").map((c) => c.text())).toEqual([
      "Fácil",
      "Média",
      "Difícil",
    ]);
  });

  it('pacote local com permissão emite "remover" com o pacote', async () => {
    const pacote = {
      id: "x",
      name: "Revisão",
      kind: "local",
      question_count: 1,
      minigame_types: ["identification"],
      difficulties: [1],
      permissions: { delete: true },
    };
    const card = montar(pacote);
    expect(card.text()).not.toContain("Já instalado");
    await card.find(".pacote-remover").trigger("click");
    expect(card.emitted("remover")[0]).toEqual([pacote]);
  });

  it("pacote vazio mostra aviso e nenhuma lista", () => {
    const card = montar({
      id: "v",
      name: "Vazio",
      kind: "local",
      question_count: 0,
      minigame_types: [],
      difficulties: [],
      permissions: { delete: true },
    });
    expect(card.text()).toContain("ainda não tem questões");
    expect(card.find(".chip-dificuldade").exists()).toBe(false);
  });
});
