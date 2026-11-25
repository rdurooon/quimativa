<script setup>
import { nextTick, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { callDesktop } from '../services/desktop';
import { GAME_TRANSITION, initializeTransition } from '../services/transition';
import QuickGameArtwork from '../components/QuickGameArtwork.vue';
import ConfiguredGameArtwork from '../components/ConfiguredGameArtwork.vue';
import PopupTemplate from '../components/PopupTemplate.vue';
import '../../css/menu.css';
import '../../css/transicao.css';

const router = useRouter();
const logoUrl = new URL('../../assets/quimativa-logo.png', import.meta.url).href;
let transition;
const popupAtivo = ref('');

function confirmarSaida() {
  callDesktop('sair').catch(() => window.close());
}

function pedirSaida() {
  popupAtivo.value = 'exit';
}

async function navigate(path) {
  await transition?.cover();
  await router.push(path);
  await nextTick();
  transition?.reveal();
}

function abrirPopup(nome) {
  popupAtivo.value = nome;
}

function fecharPopup() {
  popupAtivo.value = '';
}

onMounted(() => {
  transition = initializeTransition(GAME_TRANSITION);
});
</script>

<template>
  <main class="menu">
    <header class="menu-cabecalho">
      <div class="menu-marca">
        <img :src="logoUrl" alt="" />
        <span>QUIMATIVA</span>
      </div>
      <button class="btn btn-sair" type="button" aria-label="Sair" @click="pedirSaida">Sair</button>
    </header>

    <div class="menu-conteudo">
      <aside class="menu-lateral" aria-label="Opções do menu">
        <div class="menu-opcoes">
          <button class="menu-opcao" type="button" @click="abrirPopup('questions')">
            <svg viewBox="0 0 48 48" aria-hidden="true"><ellipse cx="24" cy="10" rx="15" ry="6"/><path d="M9 10v14c0 3 7 6 15 6s15-3 15-6V10M9 24v14c0 3 7 6 15 6s15-3 15-6V24"/></svg>
            <span>Banco de questões</span>
          </button>
          <button class="menu-opcao" type="button" @click="abrirPopup('settings')">
            <svg viewBox="0 0 48 48" aria-hidden="true"><path d="m20 5 8 0 2 6 5 3 6-2 4 7-5 4v6l5 4-4 7-6-2-5 3-2 6h-8l-2-6-5-3-6 2-4-7 5-4v-6l-5-4 4-7 6 2 5-3z"/><circle cx="24" cy="26" r="7"/></svg>
            <span>Configurações</span>
          </button>
        </div>
        <button class="menu-tutorial" type="button">
          <svg viewBox="0 0 48 48" aria-hidden="true"><path d="m8 11 11-5 10 5 11-5v31l-11 5-10-5-11 5Z"/><path d="M19 6v31M29 11v31M13 28l5-5 4 3 7-9 5 4"/><path d="m34 17 4 4m0-4-4 4"/></svg>
          <span>Tutorial</span>
        </button>
      </aside>

      <section class="menu-partidas" aria-label="Partidas">
        <button class="cartao-partida partida-rapida" type="button" @click="navigate('/game')">
          <QuickGameArtwork />
          <span class="cartao-titulo">Iniciar partida rápida</span>
          <span class="cartao-descricao">Inicie uma partida rápida, sem se preocupar em configurar</span>
        </button>
        <button class="cartao-partida partida-configurada" type="button" @click="navigate('/game')">
          <ConfiguredGameArtwork />
          <span class="cartao-titulo">Configurar partida</span>
          <span class="cartao-descricao">Faça ajustes para a partida antes de começar uma</span>
        </button>
      </section>
    </div>
    <PopupTemplate
      :open="popupAtivo === 'questions'"
      title="Banco de questões"
      description="Estrutura reservada para uma próxima etapa."
      search-placeholder="Pesquisar questão/pacote..."
      @close="fecharPopup"
    />
    <PopupTemplate
      :open="popupAtivo === 'settings'"
      title="Configurações"
      description="Estrutura reservada para uma próxima etapa."
      @close="fecharPopup"
    />
    <PopupTemplate
      :open="popupAtivo === 'exit'"
      title="Deseja fechar o Quimativa?"
      :show-close="false"
      size="confirm"
      @close="fecharPopup"
    >
      <div class="popup-acoes">
        <button class="popup-acao popup-acao-cancelar" type="button" @click="fecharPopup">Cancelar</button>
        <button class="popup-acao popup-acao-confirmar" type="button" @click="confirmarSaida">Fechar</button>
      </div>
    </PopupTemplate>
  </main>
</template>
