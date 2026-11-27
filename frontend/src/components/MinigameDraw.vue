<script setup>
import { ref, watch } from 'vue';
import { CircleHelp, Flame, FlaskConical, GitCompareArrows, Layers, ListOrdered, ScanSearch, Trophy, UsersRound } from '@lucide/vue';
import TeamLives from './TeamLives.vue';
import TeamRoster from './TeamRoster.vue';
import { MINIGAMES } from '../services/partidaRapida';

const props = defineProps({
  equipes: { type: Array, required: true },
  equipeAtiva: { type: String, required: true },
  minigame: { type: String, default: null },
  ativo: { type: Boolean, default: false },
});
const emit = defineEmits(['selecionado', 'voltar']);

const logo = new URL('../../assets/quimativa-logo.png', import.meta.url).href;
const icones = [FlaskConical, GitCompareArrows, Layers, ScanSearch, CircleHelp, ListOrdered];
const minigames = MINIGAMES.map(([id, nome], indice) => ({ id, nome, icone: icones[indice] }));

const quantidade = minigames.length;
const indiceFinal = 4 * quantidade + (props.minigame
  ? minigames.findIndex(({ id }) => id === props.minigame)
  : Math.floor(Math.random() * quantidade));
const simularDeslize = Math.random() < 0.18;
const faixa = Array.from({ length: indiceFinal + 4 }, (_, indice) => minigames[indice % quantidade]);
const escolhido = faixa[indiceFinal];
const concluido = ref(false);

watch(() => props.ativo, (ativo) => {
  if (ativo && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    concluirSorteio();
  }
}, { immediate: true });

function concluirSorteio() {
  if (!props.ativo || concluido.value) return;
  concluido.value = true;
  emit('selecionado', escolhido.id);
}
</script>

<template>
  <main class="minigame-sorteio">
    <img :src="logo" class="minigame-logo" alt="" />
    <section class="minigame-equipes" :style="{ '--equipes': equipes.length }" aria-label="Equipes da partida">
      <article
        v-for="equipe in equipes"
        :key="equipe.letra"
        class="minigame-equipe"
        :class="{
          'minigame-equipe-ativa': equipe.vidas > 0 && equipe.letra === equipeAtiva,
          'minigame-equipe-eliminada': equipe.vidas === 0,
        }"
        :aria-label="`Equipe ${equipe.letra}`"
      >
        <UsersRound class="minigame-equipe-icone" aria-hidden="true" />
        <h2>Equipe {{ equipe.letra }}</h2>
        <div class="minigame-equipe-status">
          <TeamLives :vidas="equipe.vidas" />
          <span v-if="equipe.vidas === 0" class="minigame-turno">Eliminada</span>
          <span v-else-if="equipe.letra === equipeAtiva" class="minigame-turno">Equipe da vez</span>
        </div>
        <p class="minigame-alunos">Alunos</p>
        <TeamRoster class="minigame-alunos-lista" :alunos="equipe.alunos" :equipe="equipe.letra" />
        <dl class="minigame-placar">
          <div class="minigame-pontos">
            <dt><Trophy aria-hidden="true" /> Pontuação</dt>
            <dd>{{ equipe.pontos }}</dd>
          </div>
          <div class="minigame-sequencia">
            <dt><Flame aria-hidden="true" /> Sequência</dt>
            <dd>{{ equipe.sequencia }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <h1>{{ concluido ? 'Minigame selecionado' : 'Selecionando minigame…' }}</h1>

    <div class="minigame-roleta" :class="{ 'minigame-roleta-concluida': concluido }">
      <div class="minigame-janela" aria-hidden="true">
        <div
          class="minigame-faixa"
          :class="{
            'minigame-faixa-girando': ativo && !concluido,
            'minigame-faixa-deslize': simularDeslize,
            'minigame-faixa-parada': concluido,
          }"
          :style="{
            width: `calc(${faixa.length} * var(--passo))`,
            '--inicio': `${-200 / faixa.length}%`,
            '--quase': `${-100 * (indiceFinal - 1) / faixa.length}%`,
            '--fim': `${-100 * indiceFinal / faixa.length}%`,
            transform: concluido ? 'translateX(var(--fim))' : undefined,
          }"
          @animationend.self="concluirSorteio"
        >
          <div
            v-for="(minigame, indice) in faixa"
            :key="indice"
            class="minigame-item"
            :class="{ 'minigame-sorteado': concluido && indice === indiceFinal }"
          >
            <component :is="minigame.icone" aria-hidden="true" />
            <span>{{ minigame.nome }}</span>
          </div>
        </div>
      </div>
      <div class="minigame-marcador" aria-hidden="true"></div>
      <p class="sr-only" role="status">{{ concluido ? escolhido.nome : '' }}</p>
    </div>

    <footer class="minigame-rodape">
        <button v-if="concluido && !minigame" class="minigame-voltar" type="button" @click="$emit('voltar')">
        Voltar à inscrição
      </button>
    </footer>
  </main>
</template>

<style scoped>
.minigame-sorteio {
  position: relative;
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto auto auto;
  justify-items: center;
  height: 100%;
  gap: clamp(10px, 2.3cqh, 24px);
  padding: clamp(18px, 4cqh, 46px) clamp(14px, 3cqw, 40px) 16px;
  color: var(--cor-principal-escura);
  background: radial-gradient(ellipse at 50% 90%, #dfeee4, transparent 65%);
}
.minigame-logo {
  position: absolute;
  top: clamp(18px, 4cqh, 46px);
  left: clamp(14px, 3cqw, 40px);
  width: clamp(42px, 6cqw, 74px);
  opacity: .25;
}
.minigame-equipes {
  display: grid;
  grid-template-columns: repeat(var(--equipes), minmax(0, 1fr));
  gap: clamp(10px, 1.4cqw, 18px);
  width: min(calc(var(--equipes) * 260px), 100% - 100px);
  margin: 0 auto;
  align-self: center;
  height: min(100%, 56cqh);
  min-height: 0;
}
.minigame-equipe {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  min-height: 0;
  padding: clamp(10px, 2.1cqh, 22px) clamp(10px, 1.5cqw, 20px);
  border: 3px solid var(--cor-principal);
  border-radius: 24px;
  background: var(--cor-superficie);
}
.minigame-equipe-ativa {
  background: linear-gradient(#edf8ef, var(--cor-superficie) 55%);
  box-shadow: 0 0 0 3px #79bf83, 0 0 16px #008e1552;
}
.minigame-turno {
  border-radius: 999px;
  padding: 3px 11px;
  background: var(--cor-principal-escura);
  color: var(--cor-texto-claro);
  font-size: clamp(.7rem, 1.15cqw, .9rem);
  font-weight: 700;
}
.minigame-equipe-icone {
  width: clamp(32px, 7cqh, 72px);
  height: clamp(32px, 7cqh, 72px);
  flex-shrink: 0;
  color: var(--cor-principal);
}
.minigame-equipe h2 { font-size: clamp(1rem, 2cqw, 1.5rem); }
.minigame-alunos { font-weight: 700; }
.minigame-equipe-status {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 3px 8px;
  min-height: 1.5em;
}
.minigame-equipe-eliminada {
  border-color: #8a908d;
  background: #ebedec;
  color: #3c4340;
}
.minigame-equipe-eliminada .minigame-equipe-icone,
.minigame-equipe-eliminada .minigame-alunos-lista { color: #4f5753; }
.minigame-equipe-eliminada .minigame-turno { background: #59615d; color: white; }
.minigame-equipe-eliminada .minigame-placar > div { background: #dce0de; color: inherit; }
.minigame-alunos-lista { color: var(--cor-texto-secundario); }
.minigame-placar {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  margin-top: 6px;
  text-align: center;
}
.minigame-placar > div {
  min-width: 0;
  padding: 7px 2px;
  border-radius: 12px;
}
.minigame-pontos { background: #e0f2e4; color: #084b18; }
.minigame-sequencia { background: #fff1d3; color: #704000; }
.minigame-placar dt {
  display: grid;
  justify-items: center;
  gap: 3px;
  font-size: clamp(.7rem, 1.15cqw, 1rem);
  font-weight: 700;
}
.minigame-placar dt svg { width: 1em; height: 1em; }
.minigame-placar dd {
  margin: 0;
  font-size: clamp(1.45rem, 3.4cqw, 2.65rem);
  line-height: 1.2;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}
.minigame-sorteio h1 {
  font-size: clamp(1.4rem, 3.3cqw, 2.35rem);
  text-align: center;
}

.minigame-roleta {
  --largura-item: clamp(150px, 22cqw, 265px);
  --distancia: 14px;
  --passo: calc(var(--largura-item) + var(--distancia));
  position: relative;
  width: min(100%, 1080px);
  height: clamp(76px, 13.5cqh, 106px);
}
.minigame-janela {
  position: absolute;
  inset: 0;
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, #000 28%, #000 72%, transparent);
}
.minigame-faixa {
  position: absolute;
  left: calc(50% - var(--largura-item) / 2);
  height: 100%;
  display: flex;
  align-items: stretch;
  gap: var(--distancia);
  transform: translateX(var(--inicio));
}
.minigame-faixa-girando { animation: sortear-minigame 5s cubic-bezier(.12, .65, .16, 1) both; }
.minigame-faixa-girando.minigame-faixa-deslize { animation-name: deslizar-minigame; }
@keyframes sortear-minigame {
  from { transform: translateX(var(--inicio)); }
  to { transform: translateX(var(--fim)); }
}
@keyframes deslizar-minigame {
  0% { transform: translateX(var(--inicio)); }
  81%, 87% { transform: translateX(var(--quase)); }
  100% { transform: translateX(var(--fim)); }
}
.minigame-item {
  flex: 0 0 var(--largura-item);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid #bfd9c5;
  border-radius: 20px;
  background: var(--cor-superficie);
  padding: 10px 14px;
  text-align: center;
  font-size: clamp(.95rem, 1.75cqw, 1.4rem);
  line-height: 1.15;
  font-weight: 700;
  color: var(--cor-principal);
}
.minigame-item svg { flex-shrink: 0; width: 1.1em; height: 1.1em; }
.minigame-faixa .minigame-sorteado { background: #e3f4e6; color: var(--cor-principal-escura); }
.minigame-marcador {
  position: absolute;
  inset: 0;
  width: var(--largura-item);
  margin-inline: auto;
  border: 4px solid var(--cor-principal);
  border-radius: 22px;
  pointer-events: none;
}
.minigame-marcador::before {
  position: absolute;
  top: -3px;
  left: 50%;
  width: 17px;
  height: 10px;
  background: var(--cor-principal-escura);
  clip-path: polygon(0 0, 100% 0, 50% 100%);
  transform: translateX(-50%);
  content: '';
}
.minigame-roleta-concluida .minigame-marcador { box-shadow: 0 0 13px #008e1552; }
.minigame-rodape { min-height: 34px; }
.minigame-voltar {
  padding: 5px 16px;
  border: 2px solid var(--cor-principal);
  border-radius: 999px;
  background: var(--cor-superficie);
  color: inherit;
  font: 700 .9rem var(--fonte);
  cursor: pointer;
}
.minigame-voltar:hover { background: #e8f4ea; }

@container partida (max-width: 740px) {
  .minigame-logo { display: none; }
  .minigame-equipes { width: 100%; }
}
@container partida (max-width: 530px) {
  .minigame-equipes { height: 100%; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-rows: minmax(0, 1fr); }
  .minigame-equipe { padding: 6px; gap: 2px; }
  .minigame-equipe-icone { width: 28px; height: 28px; }
  .minigame-placar dd { font-size: 1.15rem; }
}
</style>
