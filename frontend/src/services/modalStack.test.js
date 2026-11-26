import { describe, expect, it } from "vitest";
import { ref } from "vue";
import {
  activateModal,
  deactivateModal,
  getModalIndex,
  getTopModal,
} from "./modalStack";

describe("modalStack", () => {
  it("reativar um modal que já estava na pilha o leva ao topo", () => {
    // O PopupTemplate registra o ref do painel, por isso o teste usa refs.
    const banco = ref(null);
    const formulario = ref(null);
    activateModal(formulario);
    activateModal(banco);
    expect(getTopModal()).toBe(banco);

    activateModal(formulario);
    expect(getTopModal()).toBe(formulario);
    expect(getModalIndex(formulario)).toBeGreaterThan(getModalIndex(banco));

    deactivateModal(formulario);
    deactivateModal(banco);
  });
});
