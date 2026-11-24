import { afterEach, describe, expect, it, vi } from 'vitest';
import { callDesktop, isDesktopAvailable, waitForDesktop } from './desktop';

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
});
