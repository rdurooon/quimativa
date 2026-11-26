<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { ArrowLeft, Flag, Plus, UsersRound, X } from '@lucide/vue';
import { useRouter } from 'vue-router';
import PopupTemplate from '../components/PopupTemplate.vue';
import FirstTeamDraw from '../components/FirstTeamDraw.vue';
import MinigameDraw from '../components/MinigameDraw.vue';
import MatchQuestion from '../components/MatchQuestion.vue';
import MatchResults from '../components/MatchResults.vue';
import TeamRoster from '../components/TeamRoster.vue';
import { GAME_TRANSITION, initializeTransition } from '../services/transition';
import { aplicarResultado, minigameDoTurno, prepararCiclo, sortearQuestao } from '../services/partidaRapida';

const logo = new URL('../../assets/quimativa-logo.png', import.meta.url).href;
const router = useRouter();
const letras = ['A', 'B', 'C', 'D'];
const equipes = ref([{ letra: 'A', alunos: [] }, { letra: 'B', alunos: [] }]);
const nomes = reactive({});
const aviso = ref('');
const inscricaoConfirmada = ref(false);
const partida = ref(null);
const animacaoAtiva = ref(false);
const etapa = computed(() => partida.value?.etapa ?? 'inscricao');
const equipeDaVez = computed(() => partida.value?.ordem[partida.value.indice]);
const classificacao = computed(() => [...(partida.value?.equipes ?? [])].sort((a, b) => b.pontos - a.pontos));
const pronto = computed(() => equipes.value.every((equipe) => equipe.alunos.length));
let proximoId = 0;
let transicao;
let saindo = false;
let esperaMinigame;

onBeforeUnmount(() => window.clearTimeout(esperaMinigame));

onMounted(() => {
  transicao = initializeTransition(GAME_TRANSITION);
});

async function voltar() {
  if (saindo) return;
  saindo = true;
  await transicao?.cover();
  await router.push('/menu');
  await nextTick();
  transicao?.reveal();
}

function adicionarEquipe(letra) {
  if (letras[equipes.value.length] !== letra) return;
  equipes.value.push({ letra, alunos: [] });
  aviso.value = '';
}

function adicionarAluno(equipe) {
  const nome = (nomes[equipe.letra] ?? '').trim();
  if (!nome) return;
  equipe.alunos.push({ id: ++proximoId, nome });
  nomes[equipe.letra] = '';
  aviso.value = '';
}

function removerAluno(equipe, indice) {
  equipe.alunos.splice(indice, 1);
  aviso.value = '';
}

function removerEquipe(letra) {
  const indice = equipes.value.findIndex((equipe) => equipe.letra === letra);
  if (indice < 2) return;

  // Remover C também remove D, que depende de C para existir.
  const removidas = equipes.value.splice(indice);
  const alunos = removidas.flatMap((equipe) => equipe.alunos);
  removidas.forEach((equipe) => delete nomes[equipe.letra]);

  for (let i = alunos.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [alunos[i], alunos[j]] = [alunos[j], alunos[i]];
  }

  for (const aluno of alunos) {
    const menorEquipe = Math.min(...equipes.value.map((equipe) => equipe.alunos.length));
    const destinos = equipes.value.filter((equipe) => equipe.alunos.length === menorEquipe);
    const destino = destinos[Math.floor(Math.random() * destinos.length)];
    destino.alunos.push(aluno);
  }

  const mensagem = removidas.length === 2 ? 'Equipes C e D removidas.' : `Equipe ${letra} removida.`;
  aviso.value = alunos.length ? `${mensagem} Alunos redistribuídos.` : mensagem;
}

function comecarPartida() {
  if (!pronto.value || partida.value) return;
  inscricaoConfirmada.value = false;

  const primeira = Math.floor(Math.random() * equipes.value.length);
  const inscritas = equipes.value.map(({ letra }) => letra);
  partida.value = {
    etapa: 'equipe',
    equipes: equipes.value.map((equipe) => ({
      ...equipe, pontos: 0, sequencia: 0, vidas: 3, tempoExtra: false, anteriores: [],
    })),
    ordem: [...inscritas.slice(primeira), ...inscritas.slice(0, primeira)],
    ciclo: prepararCiclo(null, inscritas.length),
    rodada: 0,
    indice: 0,
  };
}

function selecionarMinigame() {
  const jogo = partida.value;
  jogo.minigame = minigameDoTurno(jogo.ciclo, jogo.rodada, jogo.indice);
  jogo.etapa = 'minigame';
}

function aguardarMinigame() {
  window.clearTimeout(esperaMinigame);
  esperaMinigame = window.setTimeout(carregarQuestao, 1500);
}

async function carregarQuestao() {
  const jogo = partida.value;
  if (!jogo || jogo.carregando) return;
  const equipe = jogo.equipes.find(({ letra }) => letra === equipeDaVez.value);
  jogo.carregando = true;
  try {
    const questao = await sortearQuestao(jogo.minigame, equipe.anteriores);
    if (partida.value !== jogo) return;
    equipe.anteriores.push(questao.id);
    jogo.tempo = equipe.tempoExtra ? 25 : 20;
    jogo.questao = questao;
    jogo.etapa = 'questao';
  } catch (erro) {
    if (partida.value !== jogo) return;
    jogo.erro = erro.message;
    jogo.etapa = 'erro';
  } finally {
    jogo.carregando = false;
  }
}

function registrarResultado(acertou) {
  const equipe = partida.value.equipes.find(({ letra }) => letra === equipeDaVez.value);
  aplicarResultado(equipe, acertou);
}

function avancarTurno() {
  const jogo = partida.value;
  const ativas = new Set(jogo.equipes.filter(({ vidas }) => vidas > 0).map(({ letra }) => letra));
  if (ativas.size <= 1) {
    jogo.etapa = 'resultado';
    return;
  }
  do {
    jogo.indice = (jogo.indice + 1) % jogo.ordem.length;
    if (jogo.indice === 0) {
      jogo.rodada++;
      if (jogo.rodada % jogo.ciclo.length === 0) {
        jogo.ciclo = prepararCiclo(jogo.ciclo, jogo.ordem.length);
      }
    }
  } while (!ativas.has(jogo.ordem[jogo.indice]));
  selecionarMinigame();
}

function voltarParaInscricao() {
  partida.value = null;
}
</script>

<template>
  <div class="partida-rapida-fluxo">
    <Transition name="troca-partida" mode="out-in" @after-enter="animacaoAtiva = true" @before-leave="animacaoAtiva = false">
      <main v-if="etapa === 'inscricao'" key="inscricao" class="inscricao">
        <header class="inscricao-cabecalho">
          <img :src="logo" class="inscricao-logo" alt="" />
          <h1><Flag aria-hidden="true" /> Iniciar partida rápida</h1>
          <button class="inscricao-voltar" type="button" aria-label="Voltar ao menu" @click="voltar">
            <ArrowLeft aria-hidden="true" /> Voltar
          </button>
        </header>

        <section class="inscricao-equipes" aria-label="Inscrição das equipes">
          <template v-for="(letra, indice) in letras" :key="letra">
            <article v-if="equipes[indice]" class="equipe" :aria-labelledby="`equipe-${letra}`">
              <button
                v-if="indice >= 2"
                class="equipe-remover"
                type="button"
                :aria-label="`Remover equipe ${letra}`"
                :title="letra === 'C' && equipes.length === 4 ? 'Remover equipes C e D' : `Remover equipe ${letra}`"
                @click="removerEquipe(letra)"
              ><X aria-hidden="true" /></button>
              <UsersRound class="equipe-icone" aria-hidden="true" />
              <h2 :id="`equipe-${letra}`">Equipe {{ letra }}</h2>
              <p class="equipe-rotulo">Alunos</p>
              <TeamRoster class="equipe-lista" :alunos="equipes[indice].alunos" :equipe="letra">
                <template #default="{ aluno, posicao }">
                  <button
                    type="button"
                    class="aluno-remover"
                    :aria-label="`Remover ${aluno.nome} da equipe ${letra}`"
                    @click="removerAluno(equipes[indice], posicao)"
                  ><X aria-hidden="true" /></button>
                </template>
              </TeamRoster>
              <form class="equipe-formulario" @submit.prevent="adicionarAluno(equipes[indice])">
                <input v-model="nomes[letra]" :aria-label="`Nome do aluno da equipe ${letra}`" placeholder="Adicionar aluno…" />
                <button type="submit" :aria-label="`Adicionar aluno à equipe ${letra}`" :disabled="!nomes[letra]?.trim()">
                  <Plus aria-hidden="true" />
                </button>
              </form>
            </article>
            <button
              v-else
              class="equipe equipe-adicionar"
              type="button"
              :disabled="indice !== equipes.length"
              @click="adicionarEquipe(letra)"
            >
              <UsersRound class="equipe-icone" aria-hidden="true" />
              <span>Adicionar<br />equipe {{ letra }}</span>
              <small v-if="indice !== equipes.length">Adicione a equipe C primeiro</small>
            </button>
          </template>
        </section>

        <footer class="inscricao-rodape">
          <button class="btn inscricao-comecar" type="button" :disabled="!pronto" @click="inscricaoConfirmada = true">
            Começar
          </button>
        </footer>
        <p class="sr-only" role="status">{{ aviso }}</p>
      </main>
      <FirstTeamDraw
        v-else-if="etapa === 'equipe'"
        key="sorteio"
        :equipes="partida.equipes"
        :primeira-equipe="partida.ordem[0]"
        :ativo="animacaoAtiva"
        @concluido="selecionarMinigame"
      />
      <MinigameDraw
        v-else-if="etapa === 'minigame'"
        :key="`minigame-${partida.rodada}-${partida.indice}`"
        :equipes="partida.equipes"
        :equipe-ativa="equipeDaVez"
        :minigame="partida.minigame"
        :ativo="animacaoAtiva"
        @selecionado="aguardarMinigame"
      />
      <MatchQuestion
        v-else-if="etapa === 'questao'"
        :key="`questao-${partida.rodada}-${partida.indice}`"
        :questao="partida.questao"
        :equipes="partida.equipes"
        :equipe-ativa="equipeDaVez"
        :tempo="partida.tempo"
        :ativo="animacaoAtiva"
        @resultado="registrarResultado"
        @avancar="avancarTurno"
      />
      <main v-else-if="etapa === 'erro'" key="erro" class="partida-status">
        <h1>Não foi possível abrir a questão</h1>
        <p role="alert">{{ partida.erro }}</p>
        <button class="btn" type="button" :disabled="partida.carregando" @click="carregarQuestao">Tentar novamente</button>
        <button class="btn" type="button" @click="voltarParaInscricao">Voltar à inscrição</button>
      </main>
      <MatchResults
        v-else
        key="resultado"
        :classificacao="classificacao"
        @repetir="voltarParaInscricao"
        @menu="voltar"
      />
    </Transition>

    <PopupTemplate
      :open="inscricaoConfirmada"
      title="Deseja começar a partida?"
      :show-close="false"
      size="confirm"
      @close="inscricaoConfirmada = false"
    >
      <div class="popup-acoes">
        <button class="popup-acao popup-acao-cancelar" type="button" @click="inscricaoConfirmada = false">
          Cancelar
        </button>
        <button class="popup-acao popup-acao-confirmar" type="button" @click="comecarPartida">
          Começar
        </button>
      </div>
    </PopupTemplate>
  </div>
</template>

<style scoped>
.partida-rapida-fluxo { height: 100%; overflow: clip; container: partida / size; }
.partida-status { min-height: 100%; display: grid; place-content: center; justify-items: center; gap: 16px; text-align: center; padding: 20px; }
.troca-partida-enter-active { transition: opacity 320ms ease 160ms; pointer-events: none; }
.troca-partida-leave-active { transition: opacity 280ms ease; pointer-events: none; }
.troca-partida-enter-from,
.troca-partida-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .troca-partida-enter-active,
  .troca-partida-leave-active { transition: none; }
}

.inscricao {
  height: 100%;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: clamp(14px, 2.7cqh, 24px);
  padding: clamp(14px, 2.3cqw, 32px);
  color: var(--cor-principal-escura);
}

.inscricao-cabecalho {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
}

.inscricao-logo { width: clamp(50px, 6cqw, 74px); opacity: .25; }
.inscricao-cabecalho h1 {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: clamp(1.25rem, 2.45cqw, 2rem);
}
.inscricao-cabecalho h1 svg { width: 1.45em; height: 1.45em; }
.inscricao-voltar {
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px clamp(10px, 2.5cqw, 34px);
  border: 2px solid var(--cor-principal);
  border-radius: 999px;
  background: var(--cor-superficie);
  color: inherit;
  font: 700 1rem var(--fonte);
  cursor: pointer;
}
.inscricao-voltar:hover { background: var(--cor-fundo); }
.inscricao-voltar svg { width: 1.1em; height: 1.1em; }

.inscricao-equipes {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(10px, 1.5cqw, 22px);
}

.equipe {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
  min-height: 0;
  padding: clamp(12px, 1.4cqw, 20px);
  border: 3px solid var(--cor-principal);
  border-radius: 24px;
  background: var(--cor-superficie);
}
.equipe-icone {
  flex-shrink: 0;
  width: clamp(58px, 8cqw, 112px);
  height: clamp(58px, 8cqw, 112px);
  margin: 10px 0;
  color: var(--cor-principal);
  stroke-width: 1.9;
}
.equipe h2 { font-size: clamp(1.15rem, 2cqw, 1.65rem); }
.equipe-rotulo { margin: 10px 0 5px; font-weight: 700; }
.equipe-adicionar {
  justify-content: flex-start;
  border-style: dashed;
  color: inherit;
  font: 700 clamp(1.1rem, 2.35cqw, 2rem) var(--fonte);
  cursor: pointer;
}
.equipe-adicionar span { margin-top: clamp(22px, 5cqh, 46px); }
.equipe-adicionar:hover:not(:disabled) { background: #e8f4ea; }
.equipe-adicionar:disabled {
  border-color: #9ba5a0;
  color: var(--cor-texto-secundario);
  cursor: default;
}
.equipe-adicionar:disabled svg { color: #78867d; }
.equipe-adicionar small { margin-top: 10px; font-size: .75rem; }
.equipe-remover {
  position: absolute;
  top: 9px;
  right: 9px;
}
.equipe-remover,
.aluno-remover,
.equipe-formulario button {
  display: grid;
  place-items: center;
  padding: 4px;
  border: 0;
  border-radius: 8px;
  color: inherit;
  background: transparent;
  cursor: pointer;
}
.equipe-remover:hover,
.aluno-remover:hover,
.equipe-formulario button:hover:not(:disabled) { background: var(--cor-fundo); }
.equipe-remover svg,
.aluno-remover svg,
.equipe-formulario button svg { width: 19px; height: 19px; }
.equipe-lista {
  color: var(--cor-texto);
}
.equipe-lista :deep(li) {
  border-bottom: 1px solid var(--cor-linha);
}
.aluno-remover { color: var(--cor-texto-secundario); }
.equipe-formulario {
  width: 100%;
  display: flex;
  align-items: center;
  margin-top: 12px;
  padding: 4px 6px 4px 10px;
  border: 2px solid #78867d;
  border-radius: 14px;
}
.equipe-formulario:focus-within {
  border-color: var(--cor-principal);
  box-shadow: 0 0 0 2px #008e1529;
}
.equipe-formulario input {
  width: 100%;
  min-width: 0;
  border: 0;
  color: var(--cor-texto);
  background: transparent;
  font: inherit;
}
.equipe-formulario input:focus-visible { outline: none; }
.equipe-formulario button:disabled { color: #78867d; cursor: default; }
.equipe-formulario button svg { stroke-width: 3; }

.inscricao-rodape { text-align: center; }
.inscricao-comecar {
  width: min(100%, 460px);
  border-radius: 18px;
  font-size: clamp(1.45rem, 3.4cqw, 2.7rem);
  text-transform: uppercase;
}
.inscricao-comecar:disabled { background: #d3dbd6; color: var(--cor-texto-secundario); cursor: default; }

@container partida (max-width: 820px) {
  .inscricao-equipes { grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-rows: minmax(0, 1fr); }
  .equipe-icone { width: 42px; height: 42px; margin-block: 4px; }
  .equipe-adicionar span { margin-top: 10px; }
}

@container partida (max-width: 440px) {
  .inscricao-cabecalho { grid-template-columns: 1fr auto; }
  .inscricao-logo { display: none; }
  .inscricao-cabecalho h1 svg { display: none; }
}
</style>
