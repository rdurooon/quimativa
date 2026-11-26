import { describe, expect, it } from 'vitest';
import router from './index';

describe('router', () => {
  it('uses hash history and declares the initial screens', () => {
    expect(router.options.history).toBeDefined();
    expect(router.getRoutes().map((route) => route.path).sort()).toEqual([
      '/',
      '/game',
      '/game/quick',
      '/menu',
    ]);
  });
});
