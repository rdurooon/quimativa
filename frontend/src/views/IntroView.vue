<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import AnimatedLogo from '../components/AnimatedLogo.vue';
import PopupTemplate from '../components/PopupTemplate.vue';
import { callDesktop } from '../services/desktop';
import { initializeTransition } from '../services/transition';
import '../../css/home.css';
import '../../css/transicao.css';

const router = useRouter();
const revelado = ref(false);
const parada = ref(false);
let transition;
let revealTimer;
let logoMark;
const popupSaidaAberto = ref(false);

function getIntroDisplayed() {
  try {
    return sessionStorage.getItem('quimativa.intro-exibida') === '1';
  } catch {
    return false;
  }
}

function revelar() {
  if (revelado.value) return;
  revelado.value = true;
  try {
    sessionStorage.setItem('quimativa.intro-exibida', '1');
  } catch {
    // A introdução continua utilizável quando o armazenamento está bloqueado.
  }
}

async function iniciar() {
  if (!transition) return;
  await transition.cover();
  await router.push('/menu');
  await nextTick();
  transition.reveal();
}

function confirmarSaida() {
  callDesktop('sair').catch(() => window.close());
}

function pedirSaida() {
  popupSaidaAberto.value = true;
}

onMounted(async () => {
  transition = initializeTransition();
  parada.value = getIntroDisplayed();
  await nextTick();
  logoMark = document.querySelector('.m2');
  if (parada.value) {
    revelar();
  } else {
    logoMark?.addEventListener('animationend', revelar);
    revealTimer = window.setTimeout(revelar, 4000);
  }
});

onUnmounted(() => {
  logoMark?.removeEventListener('animationend', revelar);
  window.clearTimeout(revealTimer);
});
</script>

<template>
  <main class="home" :class="{ revelado, parada }">
    <button class="btn btn-fechar revela" type="button" aria-label="Fechar" @click="pedirSaida">Fechar</button>
    <section class="home-centro">
      <div class="home-logo"><AnimatedLogo /></div>
      <svg class="home-logotipo revela r1" viewBox="0 0 405 65" role="img" aria-label="Quimativa">
        <text x="0" y="62" font-size="88" font-weight="800" textLength="405" lengthAdjust="spacingAndGlyphs">QUIMATIVA</text>
      </svg>
      <button class="btn btn-iniciar revela r2" type="button" @click="iniciar">INICIAR</button>
    </section>
    <p class="home-equipe revela r3">Equipe Quimativa</p>
  </main>
  <PopupTemplate
    :open="popupSaidaAberto"
    title="Deseja fechar o Quimativa?"
    :show-close="false"
    size="confirm"
    @close="popupSaidaAberto = false"
  >
    <div class="popup-acoes">
      <button class="popup-acao popup-acao-cancelar" type="button" @click="popupSaidaAberto = false">Cancelar</button>
      <button class="popup-acao popup-acao-confirmar" type="button" @click="confirmarSaida">Fechar</button>
    </div>
  </PopupTemplate>
</template>
