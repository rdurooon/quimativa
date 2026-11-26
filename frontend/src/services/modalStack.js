import { reactive } from "vue";

const activeModals = reactive([]);

function updateBodyLock() {
  if (typeof document !== "undefined") {
    document.body.style.overflow = activeModals.length ? "hidden" : "";
  }
}

export function activateModal(modal) {
  // Quem abre por último fica no topo, mesmo que já estivesse na pilha.
  const index = activeModals.indexOf(modal);
  if (index !== -1) activeModals.splice(index, 1);
  activeModals.push(modal);
  updateBodyLock();
}

export function deactivateModal(modal) {
  const index = activeModals.indexOf(modal);
  if (index !== -1) activeModals.splice(index, 1);
  updateBodyLock();
}

export function getTopModal() {
  return activeModals[activeModals.length - 1] ?? null;
}

export function getModalIndex(modal) {
  return activeModals.indexOf(modal);
}
