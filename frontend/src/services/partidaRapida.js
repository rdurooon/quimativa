import { listarQuestoes, obterQuestao } from './questoes';

export const MINIGAMES = [
  ['identification', 'Identificação de função orgânica'],
  ['find_difference', 'Encontre a diferença'],
  ['card_association', 'Associação de cartas'],
  ['molecular_analysis', 'Análise molecular'],
  ['function_molecule', 'Qual molécula pertence à função?'],
  ['function_order', 'Ordem das funções'],
];

function embaralhar(itens) {
  const ordem = [...itens];
  for (let i = ordem.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [ordem[i], ordem[j]] = [ordem[j], ordem[i]];
  }
  return ordem;
}

export function prepararCiclo(anterior, totalEquipes) {
  const ids = MINIGAMES.map(([id]) => id);
  if (!anterior) return embaralhar(ids);
  // Entre ciclos, qualquer equipe posterior pode ser a última sobrevivente da rodada anterior.
  for (let tentativa = 0; tentativa < 120; tentativa++) {
    const ciclo = embaralhar(ids);
    if (ciclo.slice(0, totalEquipes).every((id, i) =>
      anterior.slice(i + 2, totalEquipes + 1).every((ultimo) => ultimo !== id),
    )) return ciclo;
  }
  return anterior;
}

export function minigameDoTurno(ciclo, rodada, indice) {
  return ciclo[(indice + ciclo.length - (rodada % ciclo.length)) % ciclo.length];
}

export function aplicarResultado(equipe, acertou) {
  equipe.tempoExtra = !acertou;
  if (acertou) {
    equipe.sequencia++;
    equipe.pontos += equipe.sequencia === 1 ? 100 : 100 + 10 * equipe.sequencia;
  } else {
    equipe.sequencia = 0;
    equipe.vidas--;
  }
}

export async function sortearQuestao(minigame, anteriores) {
  const filtros = { minigame_type: minigame, difficulty: 1, limite: 200 };
  const itens = [];
  let pagina;
  do {
    pagina = await listarQuestoes({ ...filtros, deslocamento: itens.length });
    itens.push(...pagina.items);
  } while (pagina.items.length && itens.length < pagina.total);

  const ineditas = itens.filter(({ id }) => !anteriores.includes(id));
  const disponiveis = ineditas.length ? ineditas : itens;
  const escolhida = disponiveis[Math.floor(Math.random() * disponiveis.length)];
  if (!escolhida) throw new Error('Nenhuma questão fácil está disponível para este minigame.');
  return obterQuestao(escolhida.id);
}
