<script setup>
import { Trophy, UsersRound } from '@lucide/vue';
import TeamRoster from './TeamRoster.vue';

defineProps({
  classificacao: { type: Array, required: true },
});
defineEmits(['repetir', 'menu']);

const logo = new URL('../../assets/quimativa-logo.png', import.meta.url).href;
</script>

<template>
  <main class="resultado-final">
    <header class="resultado-cabecalho">
      <img :src="logo" alt="" />
      <h1>Resultado final</h1>
      <div class="resultado-acoes">
        <button class="btn" type="button" @click="$emit('repetir')">Jogar de novo</button>
        <button class="btn resultado-menu" type="button" @click="$emit('menu')">Voltar ao menu</button>
      </div>
    </header>

    <ol class="resultado-podios" :style="{ '--equipes': classificacao.length }" aria-label="Classificação">
      <li
        v-for="(equipe, indice) in classificacao"
        :key="equipe.letra"
        class="resultado-posicao"
        :class="`resultado-posicao-${indice + 1}`"
      >
        <div class="resultado-equipe">
          <div v-if="indice === 0" class="resultado-festa" aria-label="Equipe campeã">
            <Trophy class="resultado-taca" aria-hidden="true" />
            <span class="resultado-confetes" aria-hidden="true">
              <i
                v-for="peca in 24"
                :key="peca"
                :style="{
                  '--distancia': `${(peca - 12.5) * 10}px`,
                  '--altura': `${-35 - (peca * 19) % 42}px`,
                  '--atraso': `${(peca % 8) * 50}ms`,
                }"
              ></i>
            </span>
          </div>
          <UsersRound v-else class="resultado-grupo" aria-hidden="true" />
          <h2>Equipe {{ equipe.letra }}</h2>
        </div>
        <div class="resultado-podio">
          <strong class="resultado-lugar">{{ indice + 1 }}º lugar</strong>
          <TeamRoster class="resultado-alunos" :alunos="equipe.alunos" :equipe="equipe.letra" />
          <div class="resultado-pontos">
            <span>Pontuação</span>
            <strong>{{ equipe.pontos }}</strong>
          </div>
        </div>
      </li>
    </ol>
  </main>
</template>

<style scoped>
.resultado-final {
  height: 100%;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: clamp(18px, 4cqh, 40px);
  padding: clamp(16px, 3cqw, 36px);
  color: var(--cor-principal-escura);
  background: radial-gradient(ellipse at 50% 100%, #e0efe4, transparent 70%);
}
.resultado-cabecalho {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: start;
  gap: 12px;
}
.resultado-cabecalho img { width: clamp(48px, 6cqw, 76px); opacity: .3; }
.resultado-cabecalho h1 { font-size: clamp(1.5rem, 3.2cqw, 2.7rem); text-align: center; }
.resultado-acoes { display: grid; gap: 8px; justify-self: end; }
.resultado-acoes .btn { border: 2px solid var(--cor-principal); border-radius: 999px; font-size: clamp(.85rem, 1.4cqw, 1.1rem); }
.resultado-acoes .resultado-menu { color: var(--cor-principal-escura); background: var(--cor-superficie); }
.resultado-acoes .resultado-menu:hover { background: #e4f4e7; }
.resultado-podios {
  align-self: end;
  justify-self: center;
  display: grid;
  grid-template-columns: repeat(var(--equipes), minmax(0, 1fr));
  align-items: end;
  gap: clamp(10px, 2cqw, 26px);
  width: min(100%, calc(var(--equipes) * 300px));
  list-style: none;
}
.resultado-posicao {
  --podio-altura: clamp(120px, 30cqh, 230px);
  --podio-fundo: #d7eddd;
  --podio-borda: #278a3e;
  --podio-texto: #154822;
  min-width: 0;
  text-align: center;
}
.resultado-posicao-1 {
  --podio-altura: clamp(170px, 47cqh, 380px);
  --podio-fundo: #f7dda0;
  --podio-borda: #b47a14;
  --podio-texto: #583700;
}
.resultado-posicao-2 {
  --podio-altura: clamp(155px, 42cqh, 330px);
  --podio-fundo: #e0e7ec;
  --podio-borda: #778692;
  --podio-texto: #2c3b47;
}
.resultado-posicao-3 {
  --podio-altura: clamp(135px, 36cqh, 280px);
  --podio-fundo: #f0ceb6;
  --podio-borda: #ad6638;
  --podio-texto: #652f12;
}
.resultado-equipe { display: grid; justify-items: center; gap: 4px; margin-bottom: 12px; }
.resultado-equipe h2 { font-size: clamp(1.05rem, 2cqw, 1.7rem); }
.resultado-grupo, .resultado-taca { width: clamp(42px, 7cqw, 78px); height: clamp(42px, 7cqw, 78px); }
.resultado-taca { fill: #ffe08a; stroke: #9b650a; filter: drop-shadow(0 3px 5px #9b650a38); }
.resultado-podio {
  height: var(--podio-altura);
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: clamp(9px, 2cqw, 22px);
  border: 3px solid var(--podio-borda); border-radius: 22px 22px 12px 12px;
  color: var(--podio-texto);
  background: linear-gradient(160deg, var(--podio-fundo), #ffffff 180%);
}
.resultado-posicao-1 .resultado-podio { box-shadow: 0 0 22px #b47a1440; }
.resultado-lugar { font-size: clamp(1.05rem, 2.35cqw, 1.95rem); text-transform: uppercase; }
.resultado-alunos {
  text-align: left; font-size: clamp(.88rem, 1.45cqw, 1.18rem);
}
.resultado-pontos { display: grid; font-weight: 700; }
.resultado-pontos strong { font-size: clamp(1.4rem, 3.5cqw, 3rem); line-height: 1; font-variant-numeric: tabular-nums; }
.resultado-festa { position: relative; }
.resultado-confetes { position: absolute; inset: 0; pointer-events: none; }
.resultado-confetes i {
  position: absolute; top: 52%; left: 50%; width: 7px; height: 10px; border-radius: 2px;
  background: #e4a327;
  animation: festa-podio 1800ms ease-out var(--atraso) both;
}
.resultado-confetes i:nth-child(3n) { background: #31b84b; }
.resultado-confetes i:nth-child(3n + 1) { background: #5bbacc; }
@keyframes festa-podio {
  0% { opacity: 0; transform: scale(0); }
  38% { opacity: 1; transform: translate(var(--distancia), var(--altura)) rotate(110deg); }
  100% { opacity: 0; transform: translate(var(--distancia), 100px) rotate(350deg); }
}
@container partida (max-width: 625px) {
  .resultado-cabecalho { grid-template-columns: auto 1fr; align-items: center; }
  .resultado-acoes { grid-column: 1 / -1; justify-self: center; grid-auto-flow: column; }
  .resultado-podios { gap: 6px; }
}
@media (prefers-reduced-motion: reduce) {
  .resultado-confetes { display: none; }
}
</style>
