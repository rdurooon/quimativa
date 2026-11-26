import { ref } from 'vue';
import { callDesktop, isDesktopAvailable } from './desktop';

export const telaCheia = ref(false);
export const alterandoTelaCheia = ref(false);
export const erroTelaCheia = ref('');
let versaoComando = 0;

function ajustarEscala() {
  const estilo = document.documentElement.style;
  if (!telaCheia.value) {
    estilo.removeProperty('--escala-tela-cheia');
    return;
  }
  const escala = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
  if (escala > 0) estilo.setProperty('--escala-tela-cheia', String(escala));
}

function aplicarEstado(estado) {
  telaCheia.value = estado.tela_cheia;
  ajustarEscala();
}

export async function alternarTelaCheia() {
  if (alterandoTelaCheia.value) return;
  alterandoTelaCheia.value = true;
  versaoComando++;
  erroTelaCheia.value = '';
  try {
    const estado = await callDesktop('janela_alternar_tela_cheia');
    aplicarEstado(estado);
    if (!estado.salva) erroTelaCheia.value = 'A preferência de tela cheia não pôde ser salva.';
  } catch {
    erroTelaCheia.value = 'Não foi possível alterar o modo de exibição.';
  } finally {
    alterandoTelaCheia.value = false;
  }
}

export function iniciarControlesTelaCheia() {
  let ativo = true;
  async function restaurar() {
    const versao = versaoComando;
    try {
      const estado = await callDesktop('janela_estado');
      if (ativo && versao === versaoComando && !alterandoTelaCheia.value) aplicarEstado(estado);
    } catch {
      if (ativo) erroTelaCheia.value = 'Não foi possível consultar o modo de exibição.';
    }
  }

  function teclado(evento) {
    if (evento.key !== 'F11' || !isDesktopAvailable()) return;
    evento.preventDefault();
    if (!evento.repeat) void alternarTelaCheia();
  }

  window.addEventListener('keydown', teclado, true);
  window.addEventListener('resize', ajustarEscala);
  if (isDesktopAvailable()) void restaurar();
  else window.addEventListener('pywebviewready', restaurar, { once: true });

  return () => {
    ativo = false;
    window.removeEventListener('keydown', teclado, true);
    window.removeEventListener('resize', ajustarEscala);
    window.removeEventListener('pywebviewready', restaurar);
    document.documentElement.style.removeProperty('--escala-tela-cheia');
  };
}
