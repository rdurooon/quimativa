import { reactive } from 'vue';

const activeModals = reactive([]);

function updateBodyLock() {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = activeModals.length ? 'hidden' : '';
  }
}

export function activateModal(modal) {
  if (!activeModals.includes(modal)) activeModals.push(modal);
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
