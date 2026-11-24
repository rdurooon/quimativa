import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import IntroView from './IntroView.vue';
import MenuView from './MenuView.vue';
import PopupTemplate from '../components/PopupTemplate.vue';

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: IntroView },
      { path: '/menu', component: MenuView },
    ],
  });
}

afterEach(() => {
  vi.useRealTimers();
  document.body.innerHTML = '';
  document.body.style.overflow = '';
});

describe('initial views', () => {
  it('does not close a modal that is not open when Escape is pressed', async () => {
    const wrapper = mount(PopupTemplate);

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    await flushPromises();

    expect(wrapper.emitted('close')).toBeUndefined();
    wrapper.unmount();
  });

  it('traps Tab focus inside an open modal and closes with Escape', async () => {
    vi.useFakeTimers();
    const opener = document.createElement('button');
    document.body.append(opener);
    opener.focus();
    const wrapper = mount(PopupTemplate, {
      props: { open: true, showClose: false },
      slots: {
        default: '<button data-first>Primeiro</button><button data-last>Ultimo</button>',
      },
    });
    await flushPromises();

    expect(document.activeElement?.closest('[role="dialog"]')).not.toBeNull();
    document.querySelector('[data-last]').focus();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab' }));
    expect(document.activeElement?.getAttribute('data-first')).toBe('');

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    await vi.advanceTimersByTimeAsync(220);
    expect(wrapper.emitted('close')).toHaveLength(1);

    await wrapper.setProps({ open: false });
    expect(document.activeElement).toBe(opener);
    wrapper.unmount();
  });

  it('renders the introduction', async () => {
    sessionStorage.clear();
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();
    const wrapper = mount(IntroView, { global: { plugins: [router] } });
    expect(wrapper.get('[aria-label="Quimativa"]').exists()).toBe(true);
    expect(wrapper.get('button').text()).toBe('Fechar');
    wrapper.unmount();
  });

  it('uses the confirmation popup from the introduction close button', async () => {
    sessionStorage.clear();
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();
    const wrapper = mount(IntroView, { global: { plugins: [router] } });

    await wrapper.get('[aria-label="Fechar"]').trigger('click');
    await flushPromises();

    expect(document.body.textContent).toContain('Deseja fechar o Quimativa?');
    wrapper.unmount();
  });

  it('renders the menu options', async () => {
    const router = createTestRouter();
    await router.push('/menu');
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });
    expect(wrapper.text()).toContain('Banco de questões');
    expect(wrapper.text()).toContain('Configurações');
    wrapper.unmount();
  });

  it('navigates from the introduction to the menu', async () => {
    vi.useFakeTimers();
    sessionStorage.setItem('quimativa.intro-exibida', '1');
    const router = createTestRouter();
    await router.push('/');
    await router.isReady();
    const wrapper = mount(IntroView, { global: { plugins: [router] } });

    await vi.waitFor(() => expect(wrapper.get('.btn-iniciar')).toBeTruthy());
    await wrapper.get('.btn-iniciar').trigger('click');
    await vi.advanceTimersByTimeAsync(2200);

    expect(router.currentRoute.value.path).toBe('/menu');
    wrapper.unmount();
  });

  it('opens the questions popup without changing routes', async () => {
    const router = createTestRouter();
    await router.push('/menu');
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });

    await wrapper.findAll('.menu-opcao')[0].trigger('click');
    await flushPromises();

    expect(router.currentRoute.value.path).toBe('/menu');
    expect(document.body.textContent).toContain('Banco de questões');
    expect(document.body.textContent).toContain('Estrutura reservada para uma próxima etapa.');
    document.querySelector('[aria-label="Fechar"]')?.click();
    await flushPromises();
    wrapper.unmount();
  });

  it('opens the settings popup without changing routes', async () => {
    const router = createTestRouter();
    await router.push('/menu');
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });

    await wrapper.findAll('.menu-opcao')[1].trigger('click');
    await flushPromises();

    expect(router.currentRoute.value.path).toBe('/menu');
    expect(document.body.textContent).toContain('Configurações');
    expect(document.body.textContent).toContain('Estrutura reservada para uma próxima etapa.');
    document.querySelector('[aria-label="Fechar"]')?.click();
    await flushPromises();
    wrapper.unmount();
  });

  it('shows a confirmation popup before closing from the Sair button', async () => {
    window.pywebview = { api: { sair: vi.fn() } };
    const router = createTestRouter();
    await router.push('/menu');
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });

    await wrapper.get('[aria-label="Sair"]').trigger('click');
    await flushPromises();

    expect(document.body.textContent).toContain('Deseja fechar o Quimativa?');
    expect(document.body.textContent).toContain('Cancelar');
    expect(document.body.textContent).toContain('Fechar');
    expect(window.pywebview.api.sair).not.toHaveBeenCalled();
    expect(document.querySelector('.popup-painel-confirm')).not.toBeNull();
    expect(document.querySelector('.popup-painel-confirm [aria-label="Fechar"]')).toBeNull();

    const fechar = Array.from(document.querySelectorAll('button'))
      .find((button) => button.textContent?.trim() === 'Fechar');
    fechar?.click();
    await new Promise((resolve) => window.setTimeout(resolve, 240));
    expect(window.pywebview.api.sair).toHaveBeenCalledOnce();

    delete window.pywebview;
    wrapper.unmount();
  });

});
