<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { UsersRound } from '@lucide/vue';
import TeamLives from './TeamLives.vue';
import TeamRoster from './TeamRoster.vue';

const props = defineProps({
  equipes: { type: Array, required: true },
  primeiraEquipe: { type: String, required: true },
  ativo: { type: Boolean, default: false },
});
const emit = defineEmits(['concluido']);

const logo = new URL('../../assets/quimativa-logo.png', import.meta.url).href;
const concluido = ref(false);
const movimentoReduzido = ref(false);
const ponteiro = ref(null);
const equipeApontada = ref(null);
const centro = 200;
const raio = 190;
let quadro;
let proximaTela;

function ponto(angulo, raio) {
  const radianos = angulo * Math.PI / 180;
  return {
    x: centro + Math.cos(radianos) * raio,
    y: centro + Math.sin(radianos) * raio,
  };
}

const setores = computed(() => {
  const quantidade = props.equipes.length;
  const abertura = 360 / quantidade;
  const inicio = quantidade === 2 ? 180 : -90;
  return props.equipes.map(({ letra }, indice) => {
    const angulo = inicio + abertura * indice;
    const divisoria = ponto(angulo - abertura / 2, raio);
    const limiteFinal = ponto(angulo + abertura / 2, raio);
    return {
      letra,
      angulo,
      divisoria,
      area: `M${centro} ${centro} L${divisoria.x} ${divisoria.y} A${raio} ${raio} 0 0 1 ${limiteFinal.x} ${limiteFinal.y} Z`,
      rotulo: ponto(angulo, 126),
    };
  });
});
const anguloFinal = computed(() => {
  const alvo = setores.value.find(({ letra }) => letra === props.primeiraEquipe);
  return `${6 * 360 + alvo.angulo}deg`;
});
const setorAtivo = computed(() => setores.value.find(({ letra }) => letra === equipeApontada.value));

function acompanharSetor() {
  const matriz = window.getComputedStyle(ponteiro.value).transform;
  // A matriz CSS reflete a posição renderizada, inclusive durante a desaceleração.
  if (matriz?.startsWith('matrix')) {
    const [a, b] = matriz.slice(matriz.indexOf('(') + 1).split(',').map(Number);
    const angulo = Math.atan2(b, a) * 180 / Math.PI;
    const abertura = 360 / setores.value.length;
    const relativo = angulo - setores.value[0].angulo + abertura / 2;
    const normalizado = ((relativo % 360) + 360) % 360;
    equipeApontada.value = setores.value[Math.floor(normalizado / abertura)].letra;
  }
  quadro = window.requestAnimationFrame(acompanharSetor);
}

watch(() => props.ativo, (ativo) => {
  window.cancelAnimationFrame(quadro);
  if (!ativo) return;
  movimentoReduzido.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (movimentoReduzido.value) concluirSorteio();
  else quadro = window.requestAnimationFrame(acompanharSetor);
}, { immediate: true, flush: 'post' });

function concluirSorteio() {
  if (!props.ativo || concluido.value) return;
  window.cancelAnimationFrame(quadro);
  equipeApontada.value = props.primeiraEquipe;
  concluido.value = true;
  proximaTela = window.setTimeout(() => emit('concluido'), movimentoReduzido.value ? 0 : 1000);
}
onBeforeUnmount(() => {
  window.cancelAnimationFrame(quadro);
  window.clearTimeout(proximaTela);
});
</script>

<template>
  <main class="sorteio">
    <header class="sorteio-cabecalho">
      <img :src="logo" alt="" />
      <h1>Selecionando equipe<span v-if="!concluido">…</span></h1>
    </header>

    <div class="sorteio-conteudo">
      <section class="sorteio-equipes" :class="{ 'sorteio-duas-equipes': equipes.length === 2 }" aria-label="Equipes inscritas">
        <article
          v-for="equipe in equipes"
          :key="equipe.letra"
          class="sorteio-equipe"
          :class="{
            'sorteio-apontada': !concluido && equipe.letra === equipeApontada,
            'sorteio-vencedora': concluido && equipe.letra === primeiraEquipe,
          }"
          :aria-labelledby="`sorteio-equipe-${equipe.letra}`"
        >
          <UsersRound class="sorteio-icone" aria-hidden="true" />
          <h2 :id="`sorteio-equipe-${equipe.letra}`">Equipe {{ equipe.letra }}</h2>
          <TeamLives :vidas="equipe.vidas" />
          <p>Alunos</p>
          <TeamRoster :alunos="equipe.alunos" :equipe="equipe.letra" />
        </article>
      </section>

      <svg class="sorteio-roleta" viewBox="0 0 400 400" overflow="visible" aria-hidden="true">
        <circle cx="200" cy="200" r="190" class="roleta-fundo" />
        <path v-if="setorAtivo" :d="setorAtivo.area" class="roleta-setor-ativo" />
        <circle cx="200" cy="200" r="190" class="roleta-contorno" />
        <line
          v-for="setor in setores"
          :key="setor.letra"
          x1="200" y1="200"
          :x2="setor.divisoria.x" :y2="setor.divisoria.y"
          class="roleta-divisoria"
        />
        <text
          v-for="setor in setores"
          :key="setor.letra"
          :x="setor.rotulo.x" :y="setor.rotulo.y"
          class="roleta-rotulo"
          :class="{ 'roleta-rotulo-ativo': setor.letra === equipeApontada }"
        >Equipe {{ setor.letra }}</text>
        <g
          ref="ponteiro"
          class="roleta-ponteiro"
          :class="{
            'roleta-girando': ativo && !movimentoReduzido,
            'roleta-sem-movimento': concluido && movimentoReduzido,
          }"
          :style="{ '--angulo-final': anguloFinal }"
          @animationend.self="concluirSorteio"
        >
          <path class="roleta-ponteiro-contorno" d="M200 200 H282 M253 174 L282 200 253 226" />
          <path d="M200 200 H282 M253 174 L282 200 253 226" />
        </g>
        <circle cx="200" cy="200" r="10" class="roleta-eixo" />
        <g v-if="concluido && !movimentoReduzido" class="roleta-celebracao">
          <circle cx="200" cy="200" r="191" class="roleta-onda" />
          <g v-for="indice in 12" :key="indice" :transform="`rotate(${indice * 30} 200 200)`">
            <path class="roleta-particula" d="M196 17 L200 9 204 17 200 25 Z" />
          </g>
        </g>
      </svg>
    </div>

  </main>
</template>

<style scoped>
.sorteio {
  height: 100%;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: clamp(14px, 2.7cqh, 24px);
  padding: clamp(14px, 2.3cqw, 32px);
  color: var(--cor-principal-escura);
}
.sorteio-cabecalho {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
}
.sorteio-cabecalho img { width: clamp(50px, 6cqw, 74px); opacity: .25; }
.sorteio-cabecalho h1 { font-size: clamp(1.35rem, 3cqw, 2.2rem); }
.sorteio-conteudo {
  width: min(100%, 1140px);
  height: 100%;
  justify-self: center;
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  align-items: center;
  gap: clamp(18px, 5cqw, 68px);
}
.sorteio-equipes {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-auto-rows: minmax(0, 1fr);
  gap: clamp(10px, 1.6cqw, 20px);
  height: 100%;
  min-height: 0;
}
.sorteio-equipe {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 0;
  padding: clamp(10px, 1.6cqw, 22px);
  border: 3px solid var(--cor-principal);
  border-radius: 24px;
  background: var(--cor-superficie);
}
.sorteio-vencedora {
  box-shadow: 0 0 0 3px #79bf83, 0 0 16px #008e1580;
  animation: destacar-equipe 700ms ease-out;
}
.sorteio-apontada {
  box-shadow: 0 0 0 2px #79bf83;
  animation: piscar-equipe 300ms ease-out;
}
@keyframes piscar-equipe {
  from { background: #dff2e2; box-shadow: 0 0 0 3px #79bf83, 0 0 18px #008e1552; }
  to { background: var(--cor-superficie); }
}
@keyframes destacar-equipe {
  0% { transform: scale(.98); }
  35% { transform: scale(1.025); box-shadow: 0 0 0 5px #79bf83, 0 0 28px #008e1580; }
  100% { transform: scale(1); }
}
.sorteio-icone {
  width: clamp(32px, 4.3cqh, 55px);
  height: clamp(32px, 4.3cqh, 55px);
  flex-shrink: 0;
  margin-bottom: 4px;
  color: var(--cor-principal);
}
.sorteio-duas-equipes .sorteio-icone {
  width: clamp(64px, 14cqh, 106px);
  height: clamp(64px, 14cqh, 106px);
  margin-bottom: 8px;
}
.sorteio-equipe h2 { font-size: clamp(1.1rem, 2cqw, 1.65rem); }
.sorteio-equipe p { margin: 6px 0; font-weight: 700; }
.sorteio-equipe :deep(.lista-equipe) { color: var(--cor-texto); }
.sorteio-duas-equipes :deep(.lista-equipe) { font-size: clamp(1rem, 1.85cqw, 1.45rem); }
.sorteio-roleta {
  width: 100%;
  max-width: min(430px, 68cqh);
  max-height: 100%;
  justify-self: center;
  color: var(--cor-principal);
}
.roleta-fundo { fill: var(--cor-superficie); }
.roleta-setor-ativo { fill: var(--cor-principal-escura); }
.roleta-contorno { fill: none; stroke: currentColor; stroke-width: 7; }
.roleta-onda {
  fill: none;
  stroke: #31b84b;
  stroke-width: 4;
  transform-box: view-box;
  transform-origin: center;
  animation: onda-roleta 700ms ease-out both;
}
@keyframes onda-roleta {
  from { opacity: .85; transform: scale(.99); }
  to { opacity: 0; transform: scale(1.13); }
}
.roleta-particula {
  fill: var(--cor-ambar);
  animation: particula-roleta 900ms ease-out both;
}
.roleta-celebracao g:nth-child(odd) .roleta-particula { fill: #31b84b; animation-delay: 60ms; }
@keyframes particula-roleta {
  0% { opacity: 0; transform: translateY(24px) scaleY(.8); }
  22% { opacity: 1; }
  100% { opacity: 0; transform: translateY(-32px); }
}
.roleta-divisoria { stroke: currentColor; stroke-width: 2.5; stroke-dasharray: 20 15; }
.roleta-rotulo {
  fill: var(--cor-principal-escura);
  font: 700 20px var(--fonte);
  text-anchor: middle;
  dominant-baseline: central;
}
.roleta-rotulo-ativo { fill: var(--cor-texto-claro); }
.roleta-eixo { fill: currentColor; }
.roleta-ponteiro {
  transform-box: view-box;
  transform-origin: center;
  transform: rotate(-90deg);
  fill: none;
  stroke: currentColor;
  stroke-width: 8;
  stroke-linejoin: round;
  stroke-linecap: round;
}
.roleta-girando { animation: sortear-equipe 5s cubic-bezier(.13, .65, .16, 1) both; }
.roleta-ponteiro-contorno { stroke: var(--cor-principal-escura); stroke-width: 11; }
.roleta-setor-ativo ~ .roleta-ponteiro { stroke: var(--cor-texto-claro); }
.roleta-sem-movimento { transform: rotate(var(--angulo-final)); }
@keyframes sortear-equipe {
  to { transform: rotate(var(--angulo-final)); }
}

@media (prefers-reduced-motion: reduce) {
  .sorteio-vencedora,
  .sorteio-apontada,
  .roleta-onda,
  .roleta-particula { animation: none; }
  .roleta-celebracao { display: none; }
}

@container partida (max-width: 760px) {
  .sorteio-conteudo { gap: 12px; }
  .sorteio-equipe { padding: 8px; }
}
@container partida (max-width: 440px) {
  .sorteio-cabecalho { grid-template-columns: auto 1fr; gap: 10px; }
}
</style>
