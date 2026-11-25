import { afterEach, describe, expect, it, vi } from 'vitest';
import { GAME_TRANSITION, initializeTransition } from './transition';

afterEach(() => {
  vi.useRealTimers();
  document.documentElement.className = '';
  document.querySelector('.transicao-liquido')?.remove();
});

describe('transition service', () => {
  it('keeps the default timing and supports shorter game transitions', () => {
    initializeTransition();
    expect(document.documentElement.style.getPropertyValue('--duracao-cobrir')).toBe('1250ms');
    expect(document.documentElement.style.getPropertyValue('--duracao-revelar')).toBe('1100ms');

    initializeTransition(GAME_TRANSITION);
    expect(document.documentElement.style.getPropertyValue('--duracao-cobrir')).toBe('700ms');
    expect(document.documentElement.style.getPropertyValue('--duracao-revelar')).toBe('650ms');
  });

  it('starts reveal without hiding the route stage and clears transition classes afterward', async () => {
    vi.useFakeTimers();
    const transition = initializeTransition();

    transition.reveal();

    expect(document.documentElement.classList.contains('transicao-revelando')).toBe(true);

    await vi.advanceTimersByTimeAsync(1700);

    expect(document.documentElement.classList.contains('transicao-revelando')).toBe(false);
  });
});
