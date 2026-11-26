import { afterEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../services/questoes", async (importOriginal) => ({
  ...(await importOriginal()),
  criarQuestao: vi.fn(),
  atualizarQuestao: vi.fn(),
  listarAssets: vi.fn(),
}));

import {
  atualizarQuestao,
  criarQuestao,
  ErroBridge,
  listarAssets,
} from "../services/questoes";
import { useBibliotecaImagens } from "../composables/useBibliotecaImagens";
import CreateQuestionModal from "./CreateQuestionModal.vue";

const props = {
  open: true,
  pacotes: [
    { id: "base", name: "Questões-base" },
    { id: "rev", name: "Revisão" },
  ],
  minigames: [
    {
      value: "identification",
      name: "Identificação de função orgânica",
      description: "Descrição A",
    },
    {
      value: "find_difference",
      name: "Encontre a diferença",
      description: "Descrição B",
    },
  ],
  difficulties: [
    { value: 1, name: "Fácil" },
    { value: 2, name: "Média" },
    { value: 3, name: "Difícil" },
  ],
};

function botao(texto) {
  return [...document.querySelectorAll("button")].find(
    (b) => b.textContent.trim() === texto,
  );
}

async function irParaFormulario(minigame = "find_difference") {
  const select = document.querySelector("#questao-minigame");
  select.value = minigame;
  select.dispatchEvent(new Event("change"));
  await flushPromises();
  botao("Prosseguir").click();
  await flushPromises();
}

describe("CreateQuestionModal", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("lista os minigames e começa no primeiro", async () => {
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();

    const opcoes = [
      ...document.querySelectorAll("#questao-minigame option"),
    ].map((o) => o.textContent.trim());
    expect(opcoes).toEqual([
      "Identificação de função orgânica",
      "Encontre a diferença",
    ]);
    expect(document.querySelector("#questao-minigame").value).toBe(
      "identification",
    );
    expect(
      document.querySelector(".questao-descricao").textContent.trim(),
    ).toBe("Descrição A");
    wrapper.unmount();
  });

  it("prosseguir abre o formulário com pacote Nenhum e dificuldade Fácil", async () => {
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario();

    expect(document.body.textContent).toContain(
      "Minigame: Encontre a diferença",
    );
    const pacote = document.querySelector(".campo-pacote");
    expect(pacote.selectedOptions[0].textContent).toBe("Nenhum");
    expect(
      document.querySelector(".dificuldade-ativa").textContent.trim(),
    ).toBe("Fácil");
    wrapper.unmount();
  });

  it("cancelar sem alterações fecha direto", async () => {
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario();

    botao("Cancelar").click();
    await flushPromises();
    expect(wrapper.emitted("close")).toHaveLength(1);
    wrapper.unmount();
  });

  it("cancelar com alterações pede confirmação antes de descartar", async () => {
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario();

    const media = [...document.querySelectorAll(".dificuldade input")][1];
    media.checked = true;
    media.dispatchEvent(new Event("change"));
    await flushPromises();

    botao("Cancelar").click();
    await flushPromises();
    expect(wrapper.emitted("close")).toBeUndefined();
    expect(document.body.textContent).toContain("Descartar alterações?");

    botao("Continuar editando").click();
    await flushPromises();
    expect(
      document.querySelector(".dificuldade-ativa").textContent.trim(),
    ).toBe("Média");

    botao("Cancelar").click();
    await flushPromises();
    botao("Descartar").click();
    await flushPromises();
    expect(wrapper.emitted("close")).toHaveLength(1);
    wrapper.unmount();
  });

  it("justificativa começa vazia e conta como alteração", async () => {
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario();

    const campo = document.querySelector(".campo-justificativa textarea");
    expect(campo.value).toBe("");
    campo.value = "O grupo OH ligado a carbono saturado caracteriza álcool.";
    campo.dispatchEvent(new Event("input"));
    await flushPromises();

    expect(document.querySelector(".campo-contador").textContent).toBe(
      "56/2000",
    );
    botao("Cancelar").click();
    await flushPromises();
    expect(document.body.textContent).toContain("Descartar alterações?");
    wrapper.unmount();
  });

  it("salva a questão de identificação com o payload do contrato", async () => {
    useBibliotecaImagens().reiniciar();
    const etanol = {
      id: "etanol",
      name: "Etanol",
      data_uri: "data:image/svg+xml;base64,PHN2Zy8+",
      region_ids: ["grupo-oh"],
    };
    listarAssets.mockResolvedValue([etanol]);
    criarQuestao.mockReset().mockResolvedValue({ id: "q1" });
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario("identification");

    document.querySelector(".seletor-vazio").click();
    await flushPromises();
    document.querySelector(".galeria-item").click();
    await flushPromises();

    const digitar = async (campo, texto) => {
      campo.value = texto;
      campo.dispatchEvent(new Event("input"));
      await flushPromises();
    };
    await digitar(
      document.querySelector("#identificacao-enunciado"),
      "Qual função está destacada?",
    );
    const alternativas = document.querySelectorAll(
      '.form-alternativa input[type="text"]',
    );
    for (const [i, texto] of [
      "Álcool",
      "Cetona",
      "Éster",
      "Aldeído",
    ].entries()) {
      await digitar(alternativas[i], texto);
    }
    const radio = document.querySelectorAll(".form-correta input")[0];
    radio.checked = true;
    radio.dispatchEvent(new Event("change"));
    await flushPromises();

    botao("Salvar questão").click();
    await flushPromises();

    expect(criarQuestao).toHaveBeenCalledWith({
      minigame_type: "identification",
      difficulty: 1,
      statement: "Qual função está destacada?",
      payload: {
        molecule_asset_id: "etanol",
        highlight: { region_id: "grupo-oh" },
        alternatives: [
          { id: "A", label: "Álcool" },
          { id: "B", label: "Cetona" },
          { id: "C", label: "Éster" },
          { id: "D", label: "Aldeído" },
        ],
        correct_alternative_id: "A",
      },
      package_id: null,
      explanation: null,
    });
    expect(wrapper.emitted("salvo")[0]).toEqual([{ id: "q1" }]);
    wrapper.unmount();
  });

  it("não chama o backend com campos faltando e mostra os erros", async () => {
    criarQuestao.mockReset();
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario("identification");

    botao("Salvar questão").click();
    await flushPromises();

    expect(criarQuestao).not.toHaveBeenCalled();
    expect(document.body.textContent).toContain(
      "Corrija os campos destacados.",
    );
    expect(document.body.textContent).toContain(
      "Escolha a imagem da molécula.",
    );

    const enunciado = document.querySelector("#identificacao-enunciado");
    enunciado.value = "Qual função?";
    enunciado.dispatchEvent(new Event("input"));
    await flushPromises();
    expect(document.body.textContent).not.toContain("Escreva o enunciado.");
    expect(document.body.textContent).toContain(
      "Escolha a imagem da molécula.",
    );
    wrapper.unmount();
  });

  it("erro do backend aparece e o formulário continua preenchido", async () => {
    useBibliotecaImagens().reiniciar();
    listarAssets.mockResolvedValue([
      {
        id: "etanol",
        name: "Etanol",
        data_uri: "data:image/svg+xml;base64,PHN2Zy8+",
        region_ids: ["grupo-oh"],
      },
    ]);
    criarQuestao.mockReset().mockRejectedValue(
      new ErroBridge({
        codigo: "dados_invalidos",
        mensagem: "Dados inválidos",
        detalhes: [
          {
            campo: "payload",
            mensagem: "Alternativas com o mesmo texto: álcool",
          },
        ],
      }),
    );
    const wrapper = mount(CreateQuestionModal, { props });
    await flushPromises();
    await irParaFormulario("identification");

    document.querySelector(".seletor-vazio").click();
    await flushPromises();
    document.querySelector(".galeria-item").click();
    await flushPromises();
    const enunciado = document.querySelector("#identificacao-enunciado");
    enunciado.value = "Qual função?";
    enunciado.dispatchEvent(new Event("input"));
    for (const campo of document.querySelectorAll(
      '.form-alternativa input[type="text"]',
    )) {
      campo.value = "Álcool";
      campo.dispatchEvent(new Event("input"));
    }
    const radio = document.querySelectorAll(".form-correta input")[0];
    radio.checked = true;
    radio.dispatchEvent(new Event("change"));
    await flushPromises();

    botao("Salvar questão").click();
    await flushPromises();

    expect(document.body.textContent).toContain(
      "Alternativas com o mesmo texto: álcool",
    );
    expect(document.querySelector("#identificacao-enunciado").value).toBe(
      "Qual função?",
    );
    expect(wrapper.emitted("salvo")).toBeUndefined();
    wrapper.unmount();
  });

  it("edita: abre preenchido, sem pedir descarte, e salva com atualizarQuestao", async () => {
    const etanol = {
      id: "etanol",
      name: "Etanol",
      data_uri: "data:image/svg+xml;base64,PHN2Zy8+",
      region_ids: ["grupo-oh"],
    };
    const questao = {
      id: "q9",
      minigame_type: "identification",
      statement: "Qual função?",
      difficulty: 3,
      explanation: null,
      package: { id: "rev", name: "Revisão" },
      tags: ["Álcool"],
      source: {
        name: "ENEM 2023",
        reference: null,
        license: null,
        notes: null,
      },
      payload: {
        molecule_asset_id: "etanol",
        highlight: { region_id: "grupo-oh" },
        alternatives: [
          { id: "A", label: "Álcool" },
          { id: "B", label: "Cetona" },
          { id: "C", label: "Éster" },
          { id: "D", label: "Aldeído" },
        ],
        correct_alternative_id: "A",
      },
      assets: { etanol },
    };
    atualizarQuestao.mockReset().mockResolvedValue({ id: "q9" });
    criarQuestao.mockReset();
    const wrapper = mount(CreateQuestionModal, {
      props: { ...props, pacotes: [...props.pacotes], questao },
    });
    await flushPromises();

    expect(document.body.textContent).toContain("Editar questão");
    expect(document.querySelector("#questao-minigame")).toBeNull();
    expect(document.querySelector("#identificacao-enunciado").value).toBe(
      "Qual função?",
    );
    expect(
      document.querySelector(".dificuldade-ativa").textContent.trim(),
    ).toBe("Difícil");

    // Sem mudanças, Cancelar fecha direto.
    botao("Cancelar").click();
    await flushPromises();
    expect(wrapper.emitted("close")).toHaveLength(1);

    const enunciado = document.querySelector("#identificacao-enunciado");
    enunciado.value = "Qual função orgânica?";
    enunciado.dispatchEvent(new Event("input"));
    await flushPromises();
    botao("Salvar questão").click();
    await flushPromises();

    expect(criarQuestao).not.toHaveBeenCalled();
    expect(atualizarQuestao).toHaveBeenCalledWith("q9", {
      minigame_type: "identification",
      difficulty: 3,
      statement: "Qual função orgânica?",
      payload: questao.payload,
      package_id: "rev",
      explanation: null,
      tags: ["Álcool"],
      source: questao.source,
    });
    expect(wrapper.emitted("salvo")[0]).toEqual([{ id: "q9" }]);
    wrapper.unmount();
  });
});
