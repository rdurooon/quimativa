import { afterEach, describe, expect, it, vi } from 'vitest';
import { GAME_TRANSITION, initializeTransition } from './transition';

afterEach(() => {
  vi.useRealTimers();
  document.documentElement.className = '';
  document.querySelector('.transicao-liquido')?.remove();
});

describe('transition service', () => {
  it('uses the timing of each navigation even when a new view mounts under the overlay', async () => {
    const intro = initializeTransition();
    const cover = intro.cover();
    const game = initializeTransition(GAME_TRANSITION);
    expect(document.documentElement.style.getPropertyValue('--duracao-cobrir')).toBe('1250ms');
    const layers = document.querySelectorAll('.transicao-camada');
    layers[3].querySelector('path').dispatchEvent(new Event('animationend', { bubbles: true }));
    await Promise.resolve();
    expect(document.documentElement.classList.contains('transicao-entrada')).toBe(true);
    layers[3].dispatchEvent(new Event('animationend'));
    await cover;
    expect(document.documentElement.classList.contains('transicao-coberta')).toBe(true);
    const reveal = intro.reveal();
    expect(document.documentElement.style.getPropertyValue('--duracao-revelar')).toBe('1100ms');

    const nextCover = game.cover();
    expect(document.documentElement.classList.contains('transicao-revelando')).toBe(true);
    layers[0].dispatchEvent(new Event('animationend'));
    await reveal;
    await Promise.resolve();
    expect(document.documentElement.style.getPropertyValue('--duracao-cobrir')).toBe('700ms');
    layers[3].dispatchEvent(new Event('animationend'));
    await nextCover;
    const nextReveal = game.reveal();
    expect(document.documentElement.style.getPropertyValue('--duracao-revelar')).toBe('650ms');
    layers[0].dispatchEvent(new Event('animationend'));
    await nextReveal;
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
