import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../services/questoes", () => ({
  obterMetadados: vi.fn(),
  listarPacotes: vi.fn(),
  removerPacote: vi.fn(),
  listarQuestoes: vi.fn(),
  obterQuestao: vi.fn(),
  atualizarQuestao: vi.fn(),
  removerQuestao: vi.fn(),
  listarAssets: vi.fn(),
  importarSvg: vi.fn(),
  criarPacote: vi.fn(),
  errosPorCampo: vi.fn(() => ({})),
}));

import {
  criarPacote,
  listarAssets,
  listarPacotes,
  listarQuestoes,
  obterMetadados,
  obterQuestao,
  removerPacote,
  removerQuestao,
} from "../services/questoes";
import { useBibliotecaImagens } from "../composables/useBibliotecaImagens";
import QuestionBankPopup from "./QuestionBankPopup.vue";

const base = {
  id: "base",
  name: "Questões-base",
  kind: "base",
  question_count: 6,
  minigame_types: ["identification"],
  difficulties: [1],
  permissions: { delete: false },
};
const local = {
  id: "rev",
  name: "Revisão de química",
  kind: "local",
  question_count: 0,
  minigame_types: [],
  difficulties: [],
  permissions: { delete: true },
};

const questaoLocal = {
  id: "q1",
  statement: "Qual função está destacada?",
  minigame_name: "Identificação de função orgânica",
  difficulty: 2,
  difficulty_name: "Média",
  package: { id: "rev", name: "Revisão de química" },
  preview_asset: null,
  permissions: { edit: true, delete: true },
};
const questaoBase = {
  id: "q2",
  statement: "Encontre o éster.",
  minigame_name: "Encontre a diferença",
  difficulty: 1,
  difficulty_name: "Fácil",
  package: { id: "base", name: "Questões-base" },
  preview_asset: null,
  permissions: { edit: false, delete: false },
};

function textoDaPagina() {
  return document.body.textContent;
}

describe("QuestionBankPopup", () => {
  beforeEach(() => {
    obterMetadados.mockResolvedValue({
      minigames: [
        { value: "identification", name: "Identificação de função orgânica" },
      ],
      difficulties: [{ value: 1, name: "Fácil" }],
    });
    listarPacotes.mockResolvedValue([base, local]);
    removerPacote.mockReset();
    listarQuestoes.mockReset().mockResolvedValue({ items: [], total: 0 });
    removerQuestao.mockReset();
    listarAssets.mockReset().mockResolvedValue([]);
    useBibliotecaImagens().reiniciar();
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("carrega e lista os pacotes ao abrir", async () => {
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    expect(textoDaPagina()).toContain("Questões-base");
    expect(textoDaPagina()).toContain("Revisão de química");
    expect(textoDaPagina()).toContain("Fim da lista de questões/pacotes");
    wrapper.unmount();
  });

  it("filtra pelo nome ignorando acentos", async () => {
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    const busca = document.querySelector('input[type="search"]');
    busca.value = "quimica";
    busca.dispatchEvent(new Event("input"));
    await flushPromises();

    expect(textoDaPagina()).toContain("Revisão de química");
    expect(textoDaPagina()).not.toContain("Questões-base");
    wrapper.unmount();
  });

  it("confirma antes de remover e recarrega a lista", async () => {
    removerPacote.mockResolvedValue({ id: "rev" });
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    document.querySelector(".pacote-remover").click();
    await flushPromises();
    expect(removerPacote).not.toHaveBeenCalled();
    expect(textoDaPagina()).toContain('Remover o pacote "Revisão de química"?');

    listarPacotes.mockResolvedValue([base]);
    document.querySelector(".popup-acao-remover").click();
    await flushPromises();

    expect(removerPacote).toHaveBeenCalledWith("rev");
    expect(textoDaPagina()).not.toContain("Revisão de química");
    wrapper.unmount();
  });

  it("mostra o erro e permite tentar de novo", async () => {
    listarPacotes.mockRejectedValueOnce(new Error("Bridge indisponível"));
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    expect(textoDaPagina()).toContain("Bridge indisponível");
    document.querySelector(".banco-aviso button").click();
    await flushPromises();
    expect(textoDaPagina()).toContain("Questões-base");
    wrapper.unmount();
  });

  it("cria pacote pelo modal e recarrega a lista", async () => {
    criarPacote.mockResolvedValue({ id: "novo", name: "Novo" });
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    [...document.querySelectorAll(".banco-criar")]
      .find((b) => b.textContent.includes("Criar pacote"))
      .click();
    await flushPromises();
    expect(document.body.textContent).toContain("Criar novo pacote");

    listarPacotes.mockResolvedValue([
      base,
      local,
      { ...local, id: "novo", name: "Novo" },
    ]);
    const campo = document.querySelector("#novo-pacote-nome");
    campo.value = "Novo";
    campo.dispatchEvent(new Event("input"));
    await flushPromises();
    document.querySelector(".popup-acao-confirmar").click();
    await flushPromises();

    expect(criarPacote).toHaveBeenCalledWith("Novo");
    expect(document.body.textContent).not.toContain("Criar novo pacote");
    expect(document.body.textContent).toContain("Novo");
    wrapper.unmount();
  });

  it("fechar o Banco fecha os modais abertos sobre ele", async () => {
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();
    [...document.querySelectorAll(".banco-criar")]
      .find((b) => b.textContent.includes("Criar pacote"))
      .click();
    await flushPromises();
    expect(document.body.textContent).toContain("Criar novo pacote");

    await wrapper.setProps({ open: false });
    await flushPromises();
    await wrapper.setProps({ open: true });
    await flushPromises();

    expect(document.body.textContent).not.toContain("Criar novo pacote");
    wrapper.unmount();
  });

  it("lista as questões com minigame, pacote e dificuldade", async () => {
    listarQuestoes.mockResolvedValue({
      items: [questaoLocal, questaoBase],
      total: 2,
    });
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    expect(listarQuestoes).toHaveBeenCalledWith({
      limite: 50,
      deslocamento: 0,
    });
    const cards = document.querySelectorAll(".questao");
    expect(cards).toHaveLength(2);
    expect(cards[0].textContent).toContain("Qual função está destacada?");
    expect(cards[0].textContent).toContain("Pacote: Revisão de química");
    expect(cards[1].textContent).toContain("Pacote: Questões-base");
    // Questão-base não tem Remover.
    expect(cards[1].querySelector(".questao-remover")).toBeNull();
    wrapper.unmount();
  });

  it("a busca também procura questões no backend", async () => {
    vi.useFakeTimers();
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();
    listarQuestoes.mockClear();

    const busca = document.querySelector('input[type="search"]');
    busca.value = "alcool";
    busca.dispatchEvent(new Event("input"));
    await vi.advanceTimersByTimeAsync(300);

    expect(listarQuestoes).toHaveBeenCalledTimes(1);
    expect(listarQuestoes).toHaveBeenCalledWith({
      limite: 50,
      deslocamento: 0,
      busca: "alcool",
    });
    vi.useRealTimers();
    wrapper.unmount();
  });

  it("confirma antes de remover a questão e recarrega", async () => {
    listarQuestoes.mockResolvedValue({ items: [questaoLocal], total: 1 });
    removerQuestao.mockResolvedValue({ id: "q1" });
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    document.querySelector(".questao-remover").click();
    await flushPromises();
    expect(textoDaPagina()).toContain("Remover esta questão?");
    expect(removerQuestao).not.toHaveBeenCalled();

    listarQuestoes.mockResolvedValue({ items: [], total: 0 });
    document.querySelector(".popup-acao-remover").click();
    await flushPromises();

    expect(removerQuestao).toHaveBeenCalledWith("q1");
    expect(document.querySelectorAll(".questao")).toHaveLength(0);
    wrapper.unmount();
  });

  it("carrega a próxima página de questões", async () => {
    listarQuestoes.mockResolvedValueOnce({ items: [questaoLocal], total: 2 });
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    listarQuestoes.mockResolvedValueOnce({ items: [questaoBase], total: 2 });
    [...document.querySelectorAll("button")]
      .find((b) => b.textContent.includes("Carregar mais"))
      .click();
    await flushPromises();

    expect(listarQuestoes).toHaveBeenLastCalledWith({
      limite: 50,
      deslocamento: 1,
    });
    expect(document.querySelectorAll(".questao")).toHaveLength(2);
    expect(textoDaPagina()).toContain("Fim da lista de questões/pacotes");
    wrapper.unmount();
  });

  it("editar busca a questão completa e abre o formulário preenchido", async () => {
    listarQuestoes.mockResolvedValue({ items: [questaoLocal], total: 1 });
    obterQuestao.mockResolvedValue({
      ...questaoLocal,
      minigame_type: "find_difference",
      explanation: "Porque sim.",
      tags: [],
      source: null,
      payload: {
        molecules: [
          { id: "M1", asset_id: "etanol" },
          { id: "M2", asset_id: "propanona" },
        ],
        correct_molecule_id: "M2",
      },
      assets: {
        etanol: { id: "etanol", data_uri: "" },
        propanona: { id: "propanona", data_uri: "" },
      },
    });
    const wrapper = mount(QuestionBankPopup, { props: { open: true } });
    await flushPromises();

    document.querySelector(".questao-editar").click();
    await flushPromises();

    expect(obterQuestao).toHaveBeenCalledWith("q1");
    expect(textoDaPagina()).toContain("Editar questão");
    expect(document.querySelector("#diferenca-enunciado").value).toBe(
      "Qual função está destacada?",
    );
    wrapper.unmount();
  });
});
