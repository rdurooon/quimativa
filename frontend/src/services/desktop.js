const DEFAULT_TIMEOUT = 10000;

export function isDesktopAvailable() {
  return Boolean(window.pywebview?.api);
}

export function waitForDesktop(timeout = DEFAULT_TIMEOUT) {
  if (isDesktopAvailable()) {
    return Promise.resolve(window.pywebview.api);
  }

  return new Promise((resolve, reject) => {
    let timer;
    const onReady = () => {
      clearTimeout(timer);
      if (isDesktopAvailable()) {
        resolve(window.pywebview.api);
      } else {
        reject(new Error('A API do PyWebView está indisponível.'));
      }
    };

    window.addEventListener('pywebviewready', onReady, { once: true });
    timer = window.setTimeout(() => {
      window.removeEventListener('pywebviewready', onReady);
      reject(new Error('O PyWebView não inicializou no tempo esperado.'));
    }, timeout);
  });
}

export async function callDesktop(method, ...args) {
  const api = await waitForDesktop();
  if (typeof api[method] !== 'function') {
    throw new Error(`O método "${method}" não está disponível no PyWebView.`);
  }
  return api[method](...args);
}
