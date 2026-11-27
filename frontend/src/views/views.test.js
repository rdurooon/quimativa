import { afterEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createRouter, createMemoryHistory } from "vue-router";
import GameView from "./GameView.vue";
import IntroView from "./IntroView.vue";
import MenuView from "./MenuView.vue";
import MinigameDraw from "../components/MinigameDraw.vue";
import MatchQuestion from "../components/MatchQuestion.vue";
import MatchResults from "../components/MatchResults.vue";
import QuickGameView from "./QuickGameView.vue";
import PopupTemplate from "../components/PopupTemplate.vue";
import { listarQuestoes, obterQuestao } from "../services/questoes";
import { aplicarResultado, minigameDoTurno, prepararCiclo } from "../services/partidaRapida";
vi.mock("../services/questoes", () => ({
  obterMetadados: vi
    .fn()
    .mockResolvedValue({ minigames: [], difficulties: [] }),
  listarPacotes: vi.fn().mockResolvedValue([]),
  removerPacote: vi.fn(),
  listarQuestoes: vi.fn().mockResolvedValue({ items: [], total: 0 }),
  removerQuestao: vi.fn(),
  obterQuestao: vi.fn(),
  atualizarQuestao: vi.fn(),
  listarAssets: vi.fn().mockResolvedValue([]),
  importarSvg: vi.fn(),
}));

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: IntroView },
      { path: "/menu", component: MenuView },
      { path: "/game", component: GameView },
      { path: "/game/quick", component: QuickGameView },
    ],
  });
}

afterEach(() => {
  vi.useRealTimers();
  document.body.innerHTML = "";
  document.body.style.overflow = "";
});

describe("initial views", () => {
  it("does not close a modal that is not open when Escape is pressed", async () => {
    const wrapper = mount(PopupTemplate);

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await flushPromises();

    expect(wrapper.emitted("close")).toBeUndefined();
    wrapper.unmount();
  });

  it("traps Tab focus inside an open modal and closes with Escape", async () => {
    vi.useFakeTimers();
    const opener = document.createElement("button");
    document.body.append(opener);
    opener.focus();
    const wrapper = mount(PopupTemplate, {
      props: { open: true, showClose: false },
      slots: {
        default:
          "<button data-first>Primeiro</button><button data-last>Ultimo</button>",
      },
    });
    await flushPromises();

    expect(document.activeElement?.closest('[role="dialog"]')).not.toBeNull();
    document.querySelector("[data-last]").focus();
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Tab" }));
    expect(document.activeElement?.getAttribute("data-first")).toBe("");

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await vi.advanceTimersByTimeAsync(220);
    expect(wrapper.emitted("close")).toHaveLength(1);

    await wrapper.setProps({ open: false });
    expect(document.activeElement).toBe(opener);
    wrapper.unmount();
  });

  it("keeps the underlying modal open and focused when the top modal closes", async () => {
    vi.useFakeTimers();
    const opener = document.createElement("button");
    document.body.append(opener);
    opener.focus();
    const background = mount(PopupTemplate, {
      props: { open: true, title: "Banco de questões", showClose: false },
      slots: { default: "<button data-background>Banco</button>" },
    });
    await flushPromises();
    const backgroundButton = document.querySelector("[data-background]");

    const foreground = mount(PopupTemplate, {
      props: { open: true, title: "Criar questão", showClose: false },
      slots: { default: "<button data-foreground>Criar</button>" },
    });
    await flushPromises();

    const [backgroundOverlay, foregroundOverlay] =
      document.querySelectorAll(".popup-fundo");
    expect(backgroundOverlay.getAttribute("aria-hidden")).toBe("true");
    expect(backgroundOverlay.hasAttribute("inert")).toBe(true);
    expect(Number(foregroundOverlay.style.zIndex)).toBeGreaterThan(
      Number(backgroundOverlay.style.zIndex),
    );

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await vi.advanceTimersByTimeAsync(220);
    expect(foreground.emitted("close")).toHaveLength(1);
    expect(background.emitted("close")).toBeUndefined();

    await foreground.setProps({ open: false });
    await flushPromises();
    expect(document.querySelectorAll(".popup-fundo")).toHaveLength(1);
    expect(document.activeElement).toBe(backgroundButton);
    expect(document.body.style.overflow).toBe("hidden");

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await vi.advanceTimersByTimeAsync(220);
    expect(background.emitted("close")).toHaveLength(1);
    await background.setProps({ open: false });
    await flushPromises();
    expect(document.body.style.overflow).toBe("");

    foreground.unmount();
    background.unmount();
  });

  it("renders the introduction", async () => {
    sessionStorage.clear();
    const router = createTestRouter();
    await router.push("/");
    await router.isReady();
    const wrapper = mount(IntroView, { global: { plugins: [router] } });
    expect(wrapper.get('[aria-label="Quimativa"]').exists()).toBe(true);
    expect(wrapper.get("button").text()).toBe("Fechar");
    wrapper.unmount();
  });

  it("uses the confirmation popup from the introduction close button", async () => {
    sessionStorage.clear();
    const router = createTestRouter();
    await router.push("/");
    await router.isReady();
    const wrapper = mount(IntroView, { global: { plugins: [router] } });

    await wrapper.get('[aria-label="Fechar"]').trigger("click");
    await flushPromises();

    expect(document.body.textContent).toContain("Deseja fechar o Quimativa?");
    wrapper.unmount();
  });

  it("renders the menu options", async () => {
    const router = createTestRouter();
    await router.push("/menu");
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });
    expect(wrapper.findAll(".menu-opcao").map((botao) => botao.text())).toEqual([
      "Banco de questões", "Histórico de partidas", "Configurações",
    ]);
    await wrapper.findAll(".menu-opcao")[1].trigger("click");
    expect(document.querySelector('[role="dialog"] h1')?.textContent).toBe("Histórico de partidas");
    expect(router.currentRoute.value.path).toBe("/menu");
    wrapper.unmount();
  });

  it("navigates from the introduction to the menu", async () => {
    vi.useFakeTimers();
    sessionStorage.setItem("quimativa.intro-exibida", "1");
    const router = createTestRouter();
    await router.push("/");
    await router.isReady();
    const wrapper = mount(IntroView, { global: { plugins: [router] } });

    await vi.waitFor(() => expect(wrapper.get(".btn-iniciar")).toBeTruthy());
    await wrapper.get(".btn-iniciar").trigger("click");
    await vi.advanceTimersByTimeAsync(2200);

    expect(router.currentRoute.value.path).toBe("/menu");
    wrapper.unmount();
  });

  it("opens the questions popup without changing routes", async () => {
    const router = createTestRouter();
    await router.push("/menu");
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });

    await wrapper.findAll(".menu-opcao")[0].trigger("click");
    await flushPromises();

    expect(router.currentRoute.value.path).toBe("/menu");
    expect(document.body.textContent).toContain("Banco de questões");
    expect(document.body.textContent).toContain("Criar pacote");
    document.querySelector('[aria-label="Fechar"]')?.click();
    await flushPromises();
    wrapper.unmount();
  });

  it("opens the settings popup without changing routes", async () => {
    const router = createTestRouter();
    await router.push("/menu");
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });

    await wrapper.findAll(".menu-opcao")[2].trigger("click");
    await flushPromises();

    expect(router.currentRoute.value.path).toBe("/menu");
    expect(document.body.textContent).toContain("Configurações");
    expect(document.body.textContent).toContain(
      "Estrutura reservada para uma próxima etapa.",
    );
    document.querySelector('[aria-label="Fechar"]')?.click();
    await flushPromises();
    wrapper.unmount();
  });

  it("shows a confirmation popup before closing from the Sair button", async () => {
    window.pywebview = { api: { sair: vi.fn() } };
    const router = createTestRouter();
    await router.push("/menu");
    await router.isReady();
    const wrapper = mount(MenuView, { global: { plugins: [router] } });

    await wrapper.get('[aria-label="Sair"]').trigger("click");
    await flushPromises();

    expect(document.body.textContent).toContain("Deseja fechar o Quimativa?");
    expect(document.body.textContent).toContain("Cancelar");
    expect(document.body.textContent).toContain("Fechar");
    expect(window.pywebview.api.sair).not.toHaveBeenCalled();
    expect(document.querySelector(".popup-painel-confirm")).not.toBeNull();
    expect(
      document.querySelector('.popup-painel-confirm [aria-label="Fechar"]'),
    ).toBeNull();

    const fechar = Array.from(document.querySelectorAll("button")).find(
      (button) => button.textContent?.trim() === "Fechar",
    );
    fechar?.click();
    await new Promise((resolve) => window.setTimeout(resolve, 240));
    expect(window.pywebview.api.sair).toHaveBeenCalledOnce();

    delete window.pywebview;
    wrapper.unmount();
  });

  it("uses the faster transition when entering and leaving a game", async () => {
    const router = createTestRouter();
    await router.push("/menu");
    await router.isReady();
    const menu = mount(MenuView, { global: { plugins: [router] } });
    await flushPromises();

    await menu.get(".partida-rapida").trigger("click");
    expect(
      document.documentElement.classList.contains("transicao-entrada"),
    ).toBe(true);
    document
      .querySelectorAll(".transicao-camada")[3]
      .dispatchEvent(new Event("animationend"));
    await flushPromises();
    expect(router.currentRoute.value.path).toBe("/game/quick");
    expect(
      document.documentElement.classList.contains("transicao-revelando"),
    ).toBe(true);
    document
      .querySelectorAll(".transicao-camada")[0]
      .dispatchEvent(new Event("animationend"));
    await flushPromises();
    menu.unmount();

    const game = mount(QuickGameView, { global: { plugins: [router] } });
    await flushPromises();
    await game.get('[aria-label="Voltar ao menu"]').trigger("click");
    expect(
      document.documentElement.classList.contains("transicao-entrada"),
    ).toBe(true);
    document
      .querySelectorAll(".transicao-camada")[3]
      .dispatchEvent(new Event("animationend"));
    await flushPromises();
    expect(router.currentRoute.value.path).toBe("/menu");
    expect(
      document.documentElement.classList.contains("transicao-revelando"),
    ).toBe(true);
    document
      .querySelectorAll(".transicao-camada")[0]
      .dispatchEvent(new Event("animationend"));
    await flushPromises();
    expect(
      document.documentElement.classList.contains("transicao-revelando"),
    ).toBe(false);
    game.unmount();
  });

  it("keeps configured games separate from quick team registration", async () => {
    const router = createTestRouter();
    await router.push("/menu");
    const menu = mount(MenuView, { global: { plugins: [router] } });
    await menu.get(".partida-configurada").trigger("click");
    document.querySelectorAll(".transicao-camada")[3].dispatchEvent(new Event("animationend"));
    await flushPromises();
    expect(router.currentRoute.value.path).toBe("/game");
    document.querySelectorAll(".transicao-camada")[0].dispatchEvent(new Event("animationend"));
    await flushPromises();
    menu.unmount();
  });

  it("redistributes students from removed teams without losing or duplicating anyone", async () => {
    const router = createTestRouter();
    await router.push("/game/quick");
    const game = mount(QuickGameView, { global: { plugins: [router] } });
    const adicionarEquipe = (letra) => game.findAll(".equipe-adicionar")
      .find((button) => button.text().includes(`equipe ${letra}`));
    const alunos = (letra) => game.get(`[aria-labelledby="equipe-${letra}"]`)
      .findAll("li span").map((item) => item.text());
    async function adicionarAluno(letra, nome) {
      const cartao = game.get(`[aria-labelledby="equipe-${letra}"]`);
      await cartao.get("input").setValue(nome);
      await cartao.get("form").trigger("submit");
    }

    expect(adicionarEquipe("D").element.disabled).toBe(true);
    await adicionarEquipe("C").trigger("click");
    await adicionarEquipe("D").trigger("click");
    expect(game.get(".inscricao-comecar").element.disabled).toBe(true);
    await adicionarAluno("A", "Ana");
    await adicionarAluno("C", "Caio");
    await adicionarAluno("C", "Clara");
    await adicionarAluno("D", "Davi");
    await game.get('[aria-label="Remover equipe D"]').trigger("click");
    expect(alunos("B")).toEqual(["Davi"]);
    expect(alunos("C")).toEqual(["Caio", "Clara"]);

    await adicionarEquipe("D").trigger("click");
    await adicionarAluno("D", "Diana");
    await game.get('[aria-label="Remover equipe C"]').trigger("click");
    expect(adicionarEquipe("D").element.disabled).toBe(true);
    expect([...alunos("A"), ...alunos("B")].sort()).toEqual(["Ana", "Caio", "Clara", "Davi", "Diana"]);
    expect(Math.abs(alunos("A").length - alunos("B").length)).toBe(1);
    expect(game.get(".inscricao-comecar").element.disabled).toBe(false);
    game.unmount();
  });

  it("draws the first team and minigame and opens a question from the local bank", async () => {
    const router = createTestRouter();
    await router.push("/game/quick");
    const game = mount(QuickGameView, {
      global: { plugins: [router], stubs: { transition: false } },
    });
    for (const [letra, nome] of [["A", "Ana"], ["B", "Bruno"]]) {
      const cartao = game.get(`[aria-labelledby="equipe-${letra}"]`);
      await cartao.get("input").setValue(nome);
      await cartao.get("form").trigger("submit");
    }
    expect(game.find(".equipe-vidas").exists()).toBe(false);

    await game.get(".inscricao-comecar").trigger("click");
    expect(document.body.textContent).toContain("Deseja começar a partida?");
    document.querySelector(".popup-acao-cancelar").click();
    await flushPromises();
    expect(game.find(".sorteio").exists()).toBe(false);

    await game.get(".inscricao-comecar").trigger("click");
    const sorteio = vi.spyOn(Math, "random").mockReturnValue(0.75);
    try {
      document.querySelector(".popup-acao-confirmar").click();
      await flushPromises();
      expect(game.find(".inscricao").exists()).toBe(true);
      expect(game.find(".roleta-girando").exists()).toBe(false);
    } finally {
      sorteio.mockRestore();
    }

    await vi.waitFor(() => expect(game.find(".roleta-girando").exists()).toBe(true));
    expect(game.findAll(".sorteio-equipe [aria-label='3 vidas'] svg")).toHaveLength(6);
    expect(game.find(".minigame-voltar").exists()).toBe(false);
    expect(game.find(".sorteio-vencedora").exists()).toBe(false);
    const estiloReal = window.getComputedStyle.bind(window);
    let matriz = "matrix(-1, 0, 0, -1, 0, 0)";
    const estilo = vi.spyOn(window, "getComputedStyle").mockImplementation((elemento) =>
      elemento.classList.contains("roleta-ponteiro") ? { transform: matriz } : estiloReal(elemento),
    );
    try {
      await vi.waitFor(() => expect(game.get(".roleta-rotulo-ativo").text()).toBe("Equipe A"));
      expect(game.get(".sorteio-apontada h2").text()).toBe("Equipe A");
      matriz = "matrix(1, 0, 0, 1, 0, 0)";
      await vi.waitFor(() => expect(game.get(".roleta-rotulo-ativo").text()).toBe("Equipe B"));
      expect(game.get(".sorteio-apontada h2").text()).toBe("Equipe B");
      await game.get(".roleta-girando").trigger("animationend");
    } finally {
      estilo.mockRestore();
    }
    expect(game.get(".sorteio-vencedora h2").text()).toBe("Equipe B");
    expect(game.get(".roleta-rotulo-ativo").text()).toBe("Equipe B");
    expect(game.find(".minigame-voltar").exists()).toBe(false);
    const sorteioMinigame = vi.spyOn(Math, "random").mockReturnValue(0.75);
    try {
      await vi.waitFor(() => expect(game.find(".minigame-faixa-girando").exists()).toBe(true), { timeout: 2500 });
    } finally {
      sorteioMinigame.mockRestore();
    }
    expect(game.get(".minigame-equipe-ativa h2").text()).toBe("Equipe B");
    expect(game.get(".minigame-equipe-ativa [aria-label='3 vidas']").findAll("svg")).toHaveLength(3);
    expect(game.get(".minigame-equipe-ativa .minigame-pontos dd").text()).toBe("0");
    expect(game.get(".minigame-equipe-ativa .minigame-sequencia dd").text()).toBe("0");
    expect(game.find(".minigame-faixa-deslize").exists()).toBe(false);
    expect(game.find(".minigame-voltar").exists()).toBe(false);
    listarQuestoes.mockResolvedValueOnce({ items: [{ id: "q1" }], total: 1 });
    obterQuestao.mockResolvedValueOnce({
      id: "q1", minigame_name: "Identificação de função orgânica",
      statement: "Qual é a função?", explanation: "Contém uma carbonila.",
      payload: {
        alternatives: [{ id: "A", label: "Cetona" }, { id: "B", label: "Álcool" }],
        correct_alternative_id: "A",
      },
    });
    await game.get(".minigame-faixa-girando").trigger("animationend");
    expect(game.find(".minigame-sorteado").exists()).toBe(true);
    expect(game.find(".questao-partida").exists()).toBe(false);
    await vi.waitFor(() => expect(game.find(".questao-alternativa:enabled").exists()).toBe(true), { timeout: 2600 });
    expect(listarQuestoes).toHaveBeenLastCalledWith(expect.objectContaining({ difficulty: 1 }));
    expect(game.get(".questao-equipe-ativa").text()).toContain("Equipe B");
    expect(game.get(".questao-tempo strong").text()).toBe("20 s");
    const cetona = game.findAll(".questao-alternativa").find((opcao) => opcao.text().includes("Cetona"));
    window.dispatchEvent(new KeyboardEvent("keydown", { key: cetona.get(".questao-numero").text() }));
    await flushPromises();
    expect(game.get(".opcao-correta").text()).toContain("Cetona");
    expect(game.findAll(".questao-equipe")[1].get(".contador-placar .sr-only").text()).toBe("100");
    await vi.waitFor(() => expect(game.findAll(".questao-equipe")[1].get(".contador-valor").text()).toBe("100"), { timeout: 1200 });
    game.unmount();
  });

  it.each([2, 3, 4])("shows %i podiums and the champion's trophy", async (quantidade) => {
    const classificacao = ["C", "A", "B", "D"].slice(0, quantidade).map((letra, indice) => ({
      letra, pontos: 400 - indice * 100, alunos: [{ id: letra, nome: `Aluno ${letra}` }],
    }));
    const tela = mount(MatchResults, { props: { classificacao } });
    expect(tela.findAll(".resultado-podio")).toHaveLength(quantidade);
    expect(tela.get(".resultado-posicao-1").text()).toContain("Equipe C");
    expect(tela.findAll(".resultado-taca")).toHaveLength(1);
    await tela.get(".resultado-acoes button:first-child").trigger("click");
    await tela.get(".resultado-menu").trigger("click");
    expect(tela.emitted("repetir")).toHaveLength(1);
    expect(tela.emitted("menu")).toHaveLength(1);
    tela.unmount();
  });

  it("checks the original answer order after shuffling the displayed cards", async () => {
    const aleatorio = vi.spyOn(Math, "random").mockReturnValue(0);
    const cards = [{ id: "A", content: "Álcool" }, { id: "B", content: "Cetona" }];
    const correctOrder = ["A", "B"];
    const tela = mount(MatchQuestion, { props: {
      equipes: [], equipeAtiva: "A", tempo: 20, ativo: true,
      questao: {
        minigame_name: "Ordem das funções", statement: "Ordene as cartas",
        payload: { cards, correct_order: correctOrder },
      },
    } });
    try {
      const opcoes = tela.findAll(".questao-alternativa");
      expect(opcoes[0].text()).toContain("Cetona");
      expect(opcoes[1].text()).toContain("Álcool");
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "2" }));
      await opcoes[0].trigger("click");
      expect(tela.emitted("resultado")).toEqual([[true]]);
      expect(cards.map(({ id }) => id)).toEqual(["A", "B"]);
      expect(correctOrder).toEqual(["A", "B"]);
    } finally {
      tela.unmount();
      aleatorio.mockRestore();
    }
  });

  it("applies losses without stacking extra time and ends the feedback automatically", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval", "performance"] });
    const equipe = { letra: "A", pontos: 100, sequencia: 1, vidas: 3 };
    const tela = mount(MatchQuestion, { props: {
      equipes: [equipe], equipeAtiva: "A", tempo: 20, ativo: true,
      questao: {
        minigame_name: "Associação de cartas", statement: "Associe as cartas",
        explanation: "Estas duas cartas se correspondem.",
        payload: { cards: [{ id: "A", content: "Álcool" }, { id: "B", content: "Etanol" }], correct_pair: ["A", "B"] },
      },
    } });
    await vi.advanceTimersByTimeAsync(20000);
    expect(tela.emitted("resultado")).toEqual([[false]]);
    expect(tela.findAll(".opcao-correta")).toHaveLength(2);
    await vi.advanceTimersByTimeAsync(3000);
    expect(tela.get(".questao-justificativa").text()).toContain("Estas duas cartas");
    expect(tela.find(".justificativa-anel-correndo").exists()).toBe(false);
    await vi.advanceTimersByTimeAsync(560);
    expect(tela.find(".justificativa-anel-correndo").exists()).toBe(true);
    await vi.advanceTimersByTimeAsync(10000);
    expect(tela.find(".justificativa-fechando").exists()).toBe(true);
    expect(tela.emitted("avancar")).toBeUndefined();
    await vi.advanceTimersByTimeAsync(560);
    expect(tela.emitted("avancar")).toHaveLength(1);
    aplicarResultado(equipe, false);
    aplicarResultado(equipe, false);
    expect(equipe).toMatchObject({ pontos: 100, sequencia: 0, vidas: 1, tempoExtra: true });
    aplicarResultado(equipe, true);
    aplicarResultado(equipe, true);
    expect(equipe).toMatchObject({ pontos: 320, sequencia: 2, vidas: 1, tempoExtra: false });
    tela.unmount();
  });

  it("keeps all six minigames unique per cycle and avoids consecutive matches after eliminations", () => {
    let ciclo = prepararCiclo(null, 4);
    for (let volta = 0; volta < 10; volta++) {
      const proximo = prepararCiclo(ciclo, 4);
      for (let i = 0; i < 4; i++) {
        expect(new Set(Array.from({ length: 6 }, (_, rodada) => minigameDoTurno(ciclo, rodada, i))).size).toBe(6);
        for (let j = i + 1; j < 4; j++) {
          for (let rodada = 0; rodada < 6; rodada++) {
            expect(minigameDoTurno(ciclo, rodada, i)).not.toBe(minigameDoTurno(ciclo, rodada, j));
            const seguinte = rodada === 5 ? proximo : ciclo;
            expect(minigameDoTurno(ciclo, rodada, j)).not.toBe(minigameDoTurno(seguinte, rodada + 1, i));
          }
        }
      }
      ciclo = proximo;
    }
  });

  it.each(["click", " ", "Enter"])("skips the justification with %j and advances once", async (entrada) => {
    vi.useFakeTimers();
    const tela = mount(MatchQuestion, { props: {
      equipes: [], equipeAtiva: "A", tempo: 20, ativo: true,
      questao: {
        minigame_name: "Identificação", statement: "Escolha a alternativa",
        explanation: "Justificativa da questão.",
        payload: { alternatives: [{ id: "A", label: "Certa" }], correct_alternative_id: "A" },
      },
    } });
    const acionar = () => window.dispatchEvent(entrada === "click"
      ? new MouseEvent("click", { bubbles: true })
      : new KeyboardEvent("keydown", { key: entrada, cancelable: true }));
    try {
      await tela.get(".questao-alternativa").trigger("click");
      acionar();
      await vi.advanceTimersByTimeAsync(3560);
      expect(tela.find(".justificativa-anel-correndo").exists()).toBe(true);
      expect(document.querySelector('[role="tooltip"]')?.textContent).toBe("Clique para pular");
      acionar();
      acionar();
      await vi.advanceTimersByTimeAsync(560);
      expect(document.querySelector('[role="tooltip"]')).toBeNull();
      expect(tela.emitted("avancar")).toHaveLength(1);
      await vi.advanceTimersByTimeAsync(10000);
      expect(tela.emitted("avancar")).toHaveLength(1);
    } finally {
      tela.unmount();
    }
  });

  it("keeps the final minigame hidden until the rare slide ends", async () => {
    const aleatorio = vi.spyOn(Math, "random")
      .mockReturnValueOnce(0.75)
      .mockReturnValueOnce(0.01);
    let tela;
    try {
      tela = mount(MinigameDraw, {
        props: {
          equipes: [{ letra: "A", alunos: [], pontos: 120, sequencia: 2, vidas: 3 }],
          equipeAtiva: "A",
          ativo: true,
        },
      });
    } finally {
      aleatorio.mockRestore();
    }

    expect(tela.find(".minigame-faixa-girando.minigame-faixa-deslize").exists()).toBe(true);
    expect(tela.find(".minigame-sorteado").exists()).toBe(false);
    expect(tela.emitted("selecionado")).toBeUndefined();
    await tela.get(".minigame-faixa").trigger("animationend");
    expect(tela.get(".minigame-sorteado").text()).toBe("Qual molécula pertence à função?");
    expect(tela.emitted("selecionado")).toEqual([["function_molecule"]]);
    tela.unmount();
  });
});
