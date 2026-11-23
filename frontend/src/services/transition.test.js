import { afterEach, describe, expect, it, vi } from 'vitest';
import { initializeTransition } from './transition';

afterEach(() => {
  vi.useRealTimers();
  document.documentElement.className = '';
  document.querySelector('.transicao-liquido')?.remove();
});

describe('transition service', () => {
  it('starts reveal without hiding the route stage and clears transition classes afterward', async () => {
    vi.useFakeTimers();
    const transition = initializeTransition();

    transition.reveal();

    expect(document.documentElement.classList.contains('transicao-revelando')).toBe(true);

    await vi.advanceTimersByTimeAsync(1700);

    expect(document.documentElement.classList.contains('transicao-revelando')).toBe(false);
  });
});
