import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../services/questoes", async (importOriginal) => ({
  ...(await importOriginal()),
  criarPacote: vi.fn(),
}));

import { criarPacote, ErroBridge } from "../services/questoes";
import CreatePackageModal from "./CreatePackageModal.vue";

function campo() {
  return document.querySelector("#novo-pacote-nome");
}

function botaoCriar() {
  return document.querySelector(".popup-acao-confirmar");
}

async function digitar(texto) {
  campo().value = texto;
  campo().dispatchEvent(new Event("input"));
  await flushPromises();
}

describe("CreatePackageModal", () => {
  beforeEach(() => {
    criarPacote.mockReset();
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("só habilita Criar com nome preenchido", async () => {
    const wrapper = mount(CreatePackageModal, { props: { open: true } });
    await flushPromises();

    expect(botaoCriar().disabled).toBe(true);
    await digitar("   ");
    expect(botaoCriar().disabled).toBe(true);
    await digitar("Revisão");
    expect(botaoCriar().disabled).toBe(false);
    wrapper.unmount();
  });

  it("cria com o nome sem espaços extras e emite o pacote", async () => {
    const pacote = { id: "p1", name: "Revisão", kind: "local" };
    criarPacote.mockResolvedValue(pacote);
    const wrapper = mount(CreatePackageModal, { props: { open: true } });
    await flushPromises();

    await digitar("  Revisão  ");
    botaoCriar().click();
    await flushPromises();

    expect(criarPacote).toHaveBeenCalledWith("Revisão");
    expect(wrapper.emitted("criado")[0]).toEqual([pacote]);
    wrapper.unmount();
  });

  it("mostra o erro do backend e mantém o nome digitado", async () => {
    criarPacote.mockRejectedValue(
      new ErroBridge({
        codigo: "dados_invalidos",
        mensagem: "Dados inválidos",
        detalhes: [
          { campo: "name", mensagem: "Já existe um pacote com esse nome" },
        ],
      }),
    );
    const wrapper = mount(CreatePackageModal, { props: { open: true } });
    await flushPromises();

    await digitar("Revisão");
    botaoCriar().click();
    await flushPromises();

    expect(document.body.textContent).toContain(
      "Já existe um pacote com esse nome",
    );
    expect(campo().value).toBe("Revisão");
    expect(wrapper.emitted("criado")).toBeUndefined();
    wrapper.unmount();
  });
});
