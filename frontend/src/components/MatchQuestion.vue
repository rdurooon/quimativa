<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { UsersRound } from '@lucide/vue';
import TeamLives from './TeamLives.vue';
import AnimatedScore from './AnimatedScore.vue';
import MatchFit from './MatchFit.vue';
import { destacarRegiao } from '../utils/svgDestaque';

const props = defineProps({
  questao: { type: Object, required: true },
  equipes: { type: Array, required: true },
  equipeAtiva: { type: String, required: true },
  tempo: { type: Number, required: true },
  ativo: { type: Boolean, default: false },
});
const emit = defineEmits(['resultado', 'avancar']);
const logo = new URL('../../assets/quimativa-logo.png', import.meta.url).href;
const segundos = ref(props.tempo);
const justificativaSegundos = ref(10);
const marcadas = ref([]);
const erro = ref(null);
const resultado = ref(null);
const justificativa = ref(false);
const justificativaAtiva = ref(false);
const fechandoJustificativa = ref(false);
const movimentoReduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const duracaoSanfona = movimentoReduzido ? 0 : 380;
const duracaoTexto = movimentoReduzido ? 0 : 180;
let limite;
let cronometro;
let espera;

const payload = props.questao.payload;
const opcoes = payload.alternatives ?? payload.cards ?? payload.molecules;
const ordenacao = Boolean(payload.correct_order);
const gabarito = payload.correct_pair ?? payload.correct_order ?? [
  payload.correct_alternative_id ?? payload.correct_card_id ?? payload.correct_molecule_id,
];
const imagem = (id) => props.questao.assets?.[id]?.data_uri;
const estrutura = computed(() => destacarRegiao(imagem(payload.molecule_asset_id), payload.highlight?.region_id));

function finalizar(tipo) {
  if (resultado.value) return;
  window.clearInterval(cronometro);
  resultado.value = tipo;
  emit('resultado', tipo === 'acerto');
  espera = window.setTimeout(() => {
    justificativa.value = true;
    espera = window.setTimeout(() => {
      justificativaAtiva.value = true;
      const fim = performance.now() + 10000;
      cronometro = window.setInterval(() => {
        justificativaSegundos.value = Math.max(0, Math.ceil((fim - performance.now()) / 1000));
        if (justificativaSegundos.value === 0) encerrarJustificativa();
      }, 100);
    }, duracaoSanfona + duracaoTexto);
  }, 3000);
}

function encerrarJustificativa() {
  if (!justificativaAtiva.value) return;
  justificativaAtiva.value = false;
  window.clearInterval(cronometro);
  fechandoJustificativa.value = true;
  espera = window.setTimeout(() => emit('avancar'), duracaoTexto + duracaoSanfona);
}

function responder(id) {
  if (!props.ativo || resultado.value || marcadas.value.includes(id)) return;
  if (performance.now() >= limite) {
    segundos.value = 0;
    finalizar('tempo');
    return;
  }
  const posicao = marcadas.value.length;
  marcadas.value.push(id);
  const correta = ordenacao ? gabarito[posicao] === id : gabarito.includes(id);
  if (!correta) {
    erro.value = id;
    finalizar('erro');
  } else if (marcadas.value.length === gabarito.length) {
    finalizar('acerto');
  }
}

function teclado(evento) {
  if (evento.repeat || evento.altKey || evento.ctrlKey || evento.metaKey) return;
  if (justificativaAtiva.value && (evento.key === ' ' || evento.key === 'Enter')) {
    evento.preventDefault();
    encerrarJustificativa();
    return;
  }
  if (!/^[1-4]$/.test(evento.key)) return;
  const opcao = opcoes[Number(evento.key) - 1];
  if (opcao) {
    evento.preventDefault();
    responder(opcao.id);
  }
}

watch(() => props.ativo, (ativo) => {
  if (!ativo || limite !== undefined) return;
  limite = performance.now() + props.tempo * 1000;
  cronometro = window.setInterval(() => {
    segundos.value = Math.max(0, Math.ceil((limite - performance.now()) / 1000));
    if (segundos.value === 0) finalizar('tempo');
  }, 100);
}, { immediate: true });

onMounted(() => {
  window.addEventListener('keydown', teclado);
  window.addEventListener('click', encerrarJustificativa);
});
onBeforeUnmount(() => {
  window.removeEventListener('keydown', teclado);
  window.removeEventListener('click', encerrarJustificativa);
  window.clearInterval(cronometro);
  window.clearTimeout(espera);
});
</script>

<template>
  <main class="questao-partida">
    <svg class="questao-filtro-svg" aria-hidden="true">
      <filter id="questao-molecula-branca" color-interpolation-filters="sRGB">
        <feColorMatrix type="matrix" values="0 0 0 0 1   0 0 0 0 1   0 0 0 0 1   -.2126 -.7152 -.0722 0 1" />
        <feComposite in2="SourceAlpha" operator="in" />
      </filter>
    </svg>
    <img class="questao-marca" :src="logo" alt="" />
    <header class="questao-cabecalho">
      <h1>{{ questao.minigame_name }}</h1>
      <div class="questao-tempo" :class="{ 'tempo-curto': segundos <= tempo / 2, 'tempo-critico': segundos <= 5 }">
        <strong>{{ segundos }} s</strong>
        <div class="questao-barra" role="progressbar" aria-label="Tempo restante" :aria-valuemax="tempo" :aria-valuenow="segundos">
          <div
            class="questao-preenchimento"
            :class="{ 'questao-tempo-correndo': ativo || resultado, 'questao-tempo-pausado': resultado }"
            :style="{ '--tempo': `${tempo}s`, '--proporcao': segundos / tempo }"
          ></div>
        </div>
      </div>
    </header>

    <MatchFit class="questao-placar-area encaixe-superior">
    <aside class="questao-placar" aria-label="Placar">
      <div class="questao-turno">
        <h2>Respondendo</h2>
        <p class="questao-equipe-ativa"><UsersRound aria-hidden="true" /> Equipe {{ equipeAtiva }}</p>
      </div>
      <div class="questao-pontuacao">
        <h2>Pontuação</h2>
        <div
          v-for="equipe in equipes"
          :key="equipe.letra"
          class="questao-equipe"
          :class="{ 'questao-equipe-atual': equipe.letra === equipeAtiva }"
        >
          <div class="questao-equipe-pontos">
            <b>Equipe {{ equipe.letra }}</b>
            <strong><AnimatedScore :valor="equipe.pontos" /></strong>
          </div>
          <div class="questao-equipe-detalhes">
            <TeamLives :vidas="equipe.vidas" />
            <span>Sequência: <AnimatedScore :valor="equipe.sequencia" /></span>
          </div>
        </div>
      </div>
    </aside>
    </MatchFit>

    <MatchFit class="questao-desafio-area">
    <section class="questao-desafio" aria-label="Questão">
      <img v-if="estrutura" class="questao-molecula" :src="estrutura" alt="Estrutura molecular da questão" />
      <h2>{{ questao.statement }}</h2>
      <div class="questao-alternativas" :class="{ 'questao-cartas': !estrutura }">
        <button
          v-for="(opcao, indice) in opcoes"
          :key="opcao.id"
          type="button"
          class="questao-alternativa"
          :disabled="!ativo || !!resultado || marcadas.includes(opcao.id)"
          :class="{
            'opcao-correta': resultado && gabarito.includes(opcao.id),
            'opcao-errada': erro === opcao.id,
            'opcao-marcada': !resultado && marcadas.includes(opcao.id),
          }"
          @click="responder(opcao.id)"
        >
          <span class="questao-numero">{{ indice + 1 }}</span>
          <img v-if="imagem(opcao.asset_id)" :src="imagem(opcao.asset_id)" :alt="opcao.supplementary_text ? '' : `Estrutura da opção ${indice + 1}`" />
          <span v-if="opcao.label || opcao.content">{{ opcao.label || opcao.content }}</span>
          <small v-if="opcao.supplementary_text">{{ opcao.supplementary_text }}</small>
          <strong v-if="ordenacao && (resultado || marcadas.includes(opcao.id))" class="questao-ordem">
            {{ (resultado ? gabarito : marcadas).indexOf(opcao.id) + 1 }}º
          </strong>
          <span v-if="resultado === 'acerto' && gabarito.includes(opcao.id)" class="questao-confetes" aria-hidden="true">
            <i v-for="pedaco in 16" :key="pedaco" :style="{ '--peca': pedaco, '--atraso': `${pedaco % 4 * 45}ms` }"></i>
          </span>
        </button>
      </div>
      <p class="questao-resultado" role="status">
        <span v-if="resultado">
          {{ resultado === 'acerto' ? 'Resposta correta!' : resultado === 'tempo' ? 'Tempo esgotado!' : 'Resposta incorreta.' }}
        </span>
      </p>
    </section>
    </MatchFit>

    <section
      v-if="justificativa"
      class="questao-justificativa"
      :class="{ 'justificativa-fechando': fechandoJustificativa }"
      :style="{ '--sanfona': `${duracaoSanfona}ms`, '--texto': `${duracaoTexto}ms` }"
      aria-labelledby="turno-justificativa"
      role="status"
    >
      <MatchFit class="justificativa-conteudo">
        <h2 id="turno-justificativa">Justificativa</h2>
        <p>{{ questao.explanation || 'Esta questão não tem justificativa cadastrada.' }}</p>
        <div class="justificativa-relogio">
          <svg viewBox="0 0 80 80" aria-hidden="true">
            <circle class="justificativa-anel-base" cx="40" cy="40" r="35" />
            <circle
              class="justificativa-anel"
              :class="{ 'justificativa-anel-correndo': justificativaAtiva }"
              cx="40" cy="40" r="35" pathLength="100"
              :style="{ '--restante': (10 - justificativaSegundos) * -10 }"
            />
          </svg>
          <strong>{{ justificativaSegundos }} s</strong>
        </div>
      </MatchFit>
    </section>
  </main>
</template>

<style scoped>
.questao-partida {
  position: relative;
  display: grid;
  grid-template-columns: minmax(205px, 23%) minmax(0, 1fr) minmax(0, 7%);
  grid-template-rows: auto minmax(0, 1fr);
  gap: 16px clamp(14px, 2cqw, 28px);
  height: 100%;
  padding: clamp(12px, 2cqw, 26px);
  color: var(--cor-principal-escura);
}
.questao-marca { position: absolute; top: 20px; left: 24px; width: 6cqw; max-width: 74px; opacity: .25; }
.questao-filtro-svg { position: absolute; width: 0; height: 0; overflow: hidden; pointer-events: none; }
.questao-cabecalho { grid-column: 2; text-align: center; }
.questao-cabecalho h1 { font-size: clamp(1.25rem, 2.55cqw, 2rem); }
.questao-tempo { display: grid; text-align: right; color: var(--cor-principal-escura); font-size: 1.2rem; }
.questao-barra { width: 100%; height: 18px; border: 2px solid #45574b; border-radius: 12px; overflow: hidden; background: white; }
.questao-preenchimento {
  height: 100%;
  background: var(--cor-principal);
  transform: scaleX(var(--proporcao));
  transform-origin: left;
  transition: background-color 240ms ease;
}
.questao-tempo-correndo { animation: esvaziar-barra var(--tempo) linear both; }
.questao-tempo-pausado { animation-play-state: paused; }
.tempo-curto .questao-preenchimento { background: #dfad15; }
.tempo-critico .questao-preenchimento { background: #ba2727; }
@keyframes esvaziar-barra {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}
.questao-placar-area { grid-column: 1; grid-row: 2; }
.questao-placar { display: grid; gap: 14px; }
.questao-placar h2 { font-size: clamp(1rem, 1.55cqw, 1.28rem); }
.questao-turno { padding: 11px 14px; border-radius: 16px; background: #07551a; color: white; }
.questao-equipe-ativa { display: flex; align-items: center; gap: 8px; margin-top: 3px; font-size: clamp(1.2rem, 2.1cqw, 1.85rem); font-weight: 700; }
.questao-equipe-ativa svg { width: 1.15em; height: 1.15em; flex-shrink: 0; }
.questao-pontuacao { display: grid; gap: 6px; }
.questao-equipe { display: grid; gap: 3px; padding: 6px 10px; border: 1px solid var(--cor-linha); border-radius: 12px; background: var(--cor-superficie); }
.questao-equipe-atual { border-color: var(--cor-principal); background: #e9f5eb; }
.questao-equipe-pontos,
.questao-equipe-detalhes { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 2px 8px; }
.questao-equipe-pontos b { font-size: clamp(1rem, 1.65cqw, 1.45rem); }
.questao-equipe-pontos strong { font-size: clamp(1.35rem, 2.4cqw, 2rem); line-height: 1; }
.questao-equipe-detalhes { min-height: 23px; font-size: clamp(.8rem, 1.2cqw, 1rem); font-weight: 700; }
.questao-desafio-area { grid-column: 2; grid-row: 2; }
.questao-desafio { text-align: center; display: flex; align-items: center; flex-direction: column; gap: 12px; overflow-wrap: anywhere; }
.questao-desafio h2 { font-size: clamp(1.15rem, 2.3cqw, 1.85rem); color: var(--cor-texto); }
.questao-molecula { width: min(58%, 460px); height: clamp(65px, 23cqh, 180px); object-fit: contain; }
.questao-alternativas { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; width: 100%; }
.questao-alternativa {
  position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 5px; min-height: clamp(64px, 10cqh, 94px); padding: 8px 36px;
  border: 3px solid var(--cor-principal); border-radius: 20px; background: var(--cor-superficie);
  color: var(--cor-texto); font: 700 clamp(1rem, 2.15cqw, 1.9rem)/1.18 var(--fonte); cursor: pointer;
}
.questao-alternativa:disabled { opacity: 1; cursor: default; }
.questao-alternativa:hover:not(:disabled), .opcao-marcada { background: #e0f2e4; }
.questao-alternativa img { width: 100%; height: clamp(65px, 14cqh, 115px); object-fit: contain; }
.questao-cartas .questao-alternativa { min-height: clamp(100px, 19cqh, 155px); font-size: clamp(1rem, 1.8cqw, 1.5rem); }
.questao-numero, .questao-ordem {
  position: absolute; top: 8px; left: 8px; border-radius: 50%; min-width: 1.55em; padding: 2px;
  background: #e3f2e6; color: #084b18; font-size: clamp(.85rem, 1.55cqw, 1.15rem);
}
.questao-ordem { left: auto; right: 8px; }
.opcao-correta { background: #08751b; color: white; }
.opcao-errada { border-color: #ba2727; background: #ba2727; color: white; }
.opcao-correta img, .opcao-errada img { filter: url(#questao-molecula-branca); }
.opcao-correta .questao-numero, .opcao-correta .questao-ordem,
.opcao-errada .questao-numero, .opcao-errada .questao-ordem { background: #fff3; color: white; }
.questao-resultado { min-height: 1.3em; font-weight: 700; }
.questao-resultado span { display: inline-block; animation: mostrar-resultado 300ms ease-out both; }
@keyframes mostrar-resultado {
  from { opacity: 0; transform: translateY(7px) scale(.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.questao-confetes { position: absolute; inset: 0; pointer-events: none; }
.questao-confetes i {
  position: absolute; left: calc(var(--peca) * 5.8%); top: -13px; width: 7px; height: 10px;
  background: #f3bf26; animation: confete 1300ms ease-out both;
  animation-delay: var(--atraso);
}
.questao-confetes i:nth-child(3n) { background: #42cddd; }
.questao-confetes i:nth-child(3n + 1) { background: #f27b93; }
@keyframes confete {
  from { transform: translateY(-15px) rotate(0); }
  to { opacity: 0; transform: translateY(135px) rotate(270deg); }
}
.questao-justificativa {
  position: absolute; inset: 50% 0 auto; transform: translateY(-50%); z-index: 1;
  padding: clamp(24px, 5cqh, 44px) 8%;
  height: min(76cqh, 510px);
  border-block: 5px solid #101612;
  background: #152019eb; color: white; text-align: center;
  animation: abrir-sanfona var(--sanfona) cubic-bezier(.2, .75, .3, 1) both;
}
.justificativa-conteudo {
  height: 100%;
  animation: revelar-texto var(--texto) ease-out var(--sanfona) both;
}
.justificativa-conteudo :deep(.encaixe-conteudo) { display: grid; justify-items: center; gap: 16px; }
.questao-justificativa.justificativa-fechando {
  animation: fechar-sanfona var(--sanfona) ease-in var(--texto) both;
}
.justificativa-fechando .justificativa-conteudo { animation: ocultar-texto var(--texto) ease-in both; }
@keyframes abrir-sanfona { from { clip-path: inset(50% 0); } to { clip-path: inset(0); } }
@keyframes fechar-sanfona { from { clip-path: inset(0); } to { clip-path: inset(50% 0); } }
@keyframes revelar-texto { from { opacity: 0; } to { opacity: 1; } }
@keyframes ocultar-texto { from { opacity: 1; } to { opacity: 0; } }
.questao-justificativa h2 { font-size: clamp(1.6rem, 4.5cqw, 3.5rem); }
.questao-justificativa p { max-width: 950px; font-size: clamp(1.1rem, 2.7cqw, 2rem); overflow-wrap: anywhere; }
.justificativa-relogio { position: relative; width: 82px; aspect-ratio: 1; display: grid; place-items: center; }
.justificativa-relogio svg { position: absolute; inset: 0; width: 100%; transform: rotate(-90deg); fill: none; stroke-width: 5; }
.justificativa-relogio strong { font-size: 1.5rem; font-variant-numeric: tabular-nums; }
.justificativa-anel-base { stroke: #ffffff38; }
.justificativa-anel { stroke: white; stroke-dasharray: 100 100; stroke-dashoffset: var(--restante); }
.justificativa-anel-correndo { animation: esvaziar-anel 10s linear both; }
@keyframes esvaziar-anel { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -100; } }
@container partida (max-width: 780px) {
  .questao-partida { grid-template-columns: minmax(160px, 26%) minmax(0, 1fr); }
}
@container partida (max-width: 480px) {
  .questao-partida { grid-template-columns: minmax(92px, 24%) minmax(0, 1fr); gap: 8px; }
  .questao-cabecalho { grid-column: 1 / -1; }
  .questao-alternativa { padding-inline: 18px; }
  .questao-marca { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .questao-tempo-correndo, .justificativa-anel-correndo,
  .questao-resultado span, .questao-justificativa, .justificativa-conteudo { animation: none; }
  .questao-confetes { display: none; }
}
</style>
