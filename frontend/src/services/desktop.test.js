import { afterEach, describe, expect, it, vi } from 'vitest';
import { callDesktop, isDesktopAvailable, waitForDesktop } from './desktop';
import { iniciarControlesTelaCheia, telaCheia } from './fullscreen';

afterEach(() => {
  delete window.pywebview;
  vi.restoreAllMocks();
});

describe('desktop service', () => {
  it('detects an unavailable bridge and rejects after the timeout', async () => {
    expect(isDesktopAvailable()).toBe(false);
    await expect(waitForDesktop(1)).rejects.toThrow('não inicializou');
  });

  it('calls an available PyWebView method', async () => {
    window.pywebview = { api: { ping: vi.fn().mockResolvedValue('pong') } };
    await expect(callDesktop('ping')).resolves.toBe('pong');
    expect(window.pywebview.api.ping).toHaveBeenCalledOnce();
  });

  it('resolves when the bridge becomes ready after the call', async () => {
    const promise = waitForDesktop(100);
    window.pywebview = { api: { ping: vi.fn() } };
    window.dispatchEvent(new Event('pywebviewready'));
    await expect(promise).resolves.toBe(window.pywebview.api);
  });

  it('restores fullscreen, scales the app and handles F11 from a focused input', async () => {
    const alternar = vi.fn().mockResolvedValue({ tela_cheia: false, salva: true });
    window.pywebview = { api: {
      janela_estado: vi.fn().mockResolvedValue({ tela_cheia: true }),
      janela_alternar_tela_cheia: alternar,
    } };
    const parar = iniciarControlesTelaCheia();
    const input = document.createElement('input');
    document.body.append(input);
    try {
      await vi.waitFor(() => expect(telaCheia.value).toBe(true));
      expect(Number(document.documentElement.style.getPropertyValue('--escala-tela-cheia')))
        .toBe(Math.min(window.innerWidth / 1280, window.innerHeight / 720));
      input.focus();
      const tecla = new KeyboardEvent('keydown', { key: 'F11', bubbles: true, cancelable: true });
      expect(input.dispatchEvent(tecla)).toBe(false);
      await vi.waitFor(() => expect(telaCheia.value).toBe(false));
      expect(alternar).toHaveBeenCalledOnce();
      expect(document.documentElement.style.getPropertyValue('--escala-tela-cheia')).toBe('');
    } finally {
      input.remove();
      parar();
    }
  });
});
