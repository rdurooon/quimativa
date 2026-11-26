import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import QuestionCard from "./QuestionCard.vue";

const questao = {
  id: "q1",
  statement: "Qual função está destacada?",
  minigame_name: "Identificação de função orgânica",
  difficulty: 3,
  difficulty_name: "Difícil",
  package: null,
  permissions: { edit: true, delete: true },
};

describe("QuestionCard", () => {
  it("mostra enunciado, minigame, pacote Nenhum e dificuldade", () => {
    const card = mount(QuestionCard, { props: { questao } });
    expect(card.text()).toContain("Qual função está destacada?");
    expect(card.text()).toContain("Identificação de função orgânica");
    expect(card.text()).toContain("Pacote: Nenhum");
    expect(card.find(".questao-dificuldade-3").text()).toBe("Difícil");
  });

  it("usa a miniatura quando há imagem", () => {
    const card = mount(QuestionCard, {
      props: { questao, imagem: "data:image/svg+xml;base64,AAA" },
    });
    expect(card.find(".questao-miniatura img").attributes("src")).toBe(
      "data:image/svg+xml;base64,AAA",
    );
  });

  it("só oferece remover com permissão e emite a questão", async () => {
    const card = mount(QuestionCard, { props: { questao } });
    await card.find(".questao-remover").trigger("click");
    expect(card.emitted("remover")[0]).toEqual([questao]);

    const base = mount(QuestionCard, {
      props: {
        questao: { ...questao, permissions: { edit: false, delete: false } },
      },
    });
    expect(base.find(".questao-remover").exists()).toBe(false);
  });

  it("oferece editar só com permissão e emite a questão", async () => {
    const card = mount(QuestionCard, { props: { questao } });
    await card.find(".questao-editar").trigger("click");
    expect(card.emitted("editar")[0]).toEqual([questao]);

    const base = mount(QuestionCard, {
      props: {
        questao: { ...questao, permissions: { edit: false, delete: false } },
      },
    });
    expect(base.find(".questao-editar").exists()).toBe(false);
  });
});
