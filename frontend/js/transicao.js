(function () {
  var DURACAO_COBRIR = 1250;
  var DURACAO_REVELAR = 1100;
  var ATRASO_ULTIMA_CAMADA = 240;
  var CORES = ['#006b10', '#008e15', '#31b84b', '#a8e3ae'];
  var reduzida = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var raiz = document.documentElement;
  var overlay = document.querySelector('.transicao-liquido');

  raiz.style.setProperty('--duracao-cobrir', DURACAO_COBRIR + 'ms');
  raiz.style.setProperty('--duracao-revelar', DURACAO_REVELAR + 'ms');

  function aleatorio(seed) {
    var valor = Math.sin(seed * 12.9898) * 43758.5453;
    return valor - Math.floor(valor);
  }

  function criarBorda(seed, base, quantidade, gotas) {
    var pontos = [];
    for (var i = 0; i <= quantidade; i += 1) {
      var x = (i / quantidade) * 1000;
      var onda = Math.sin(i * 0.72 + seed) * 13;
      var variacao = (aleatorio(seed + i * 3.7) - 0.5) * 18;
      var y = base + onda + variacao;

      for (var j = 0; j < gotas.length; j += 1) {
        var distancia = Math.abs(x - gotas[j].x);
        if (distancia < gotas[j].largura) {
          var queda = 1 - distancia / gotas[j].largura;
          y += gotas[j].altura * queda * queda;
        }
      }

      pontos.push(x.toFixed(1) + ' ' + y.toFixed(1));
    }
    return pontos;
  }

  function bordaSuave(pontos) {
    var caminho = 'M' + pontos[0];
    for (var i = 1; i < pontos.length - 1; i += 1) {
      var atual = pontos[i].split(' ');
      var proximo = pontos[i + 1].split(' ');
      var meioX = ((Number(atual[0]) + Number(proximo[0])) / 2).toFixed(1);
      var meioY = ((Number(atual[1]) + Number(proximo[1])) / 2).toFixed(1);
      caminho += ' Q' + pontos[i] + ' ' + meioX + ' ' + meioY;
    }
    return caminho + ' Q' + pontos[pontos.length - 1] + ' ' + pontos[pontos.length - 1];
  }

  function criarGotas(indice) {
    var gotas = [];
    for (var i = 0; i < 6; i += 1) {
      gotas.push({
        x: 55 + aleatorio(indice * 23 + i + 1) * 890,
        largura: 13 + aleatorio(indice * 29 + i + 5) * 26,
        altura: 45 + aleatorio(indice * 41 + i + 9) * 105
      });
    }
    return gotas;
  }

  function caminhoMassa(indice) {
    var gotas = criarGotas(indice);
    var topo = criarBorda(indice + 20, 32 + indice * 5, 28, []);
    var fundo = criarBorda(indice + 2, 1160 + indice * 9, 28, gotas).reverse();
    return bordaSuave(topo) + ' L1000 1400 ' + bordaSuave(fundo).replace(/^M/, 'L') + ' Z';
  }

  function criarCamada(indice) {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 1000 1400');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.className.baseVal = 'transicao-camada';
    svg.innerHTML =
      '<path fill="' + CORES[indice] + '" d="' + caminhoMassa(indice) + '"/>' +
      (indice === 2
        ? '<g class="transicao-quimica"><circle class="transicao-bolha-svg" cx="230" cy="500" r="10"/><circle class="transicao-bolha-svg" cx="810" cy="720" r="6"/><path class="transicao-molecula" d="m640 470 28-16 28 16v32l-28 16-28-16z m28-16v-28 m28 44 26 15 m-54 13-25 16"/></g>'
        : '');
    return svg;
  }

  function preparar() {
    if (!overlay || overlay.querySelector('.transicao-camada')) return;
    for (var i = 0; i < CORES.length; i += 1) {
      overlay.appendChild(criarCamada(i));
    }
  }

  preparar();

  function cobrir(depois) {
    raiz.classList.remove('transicao-coberta', 'transicao-revelando');
    raiz.classList.add('transicao-entrada');
    window.setTimeout(depois, reduzida ? 250 : DURACAO_COBRIR + ATRASO_ULTIMA_CAMADA + 350);
  }

  function revelar(depois) {
    raiz.classList.remove('transicao-entrada');
    raiz.classList.add('transicao-revelando');
    window.setTimeout(function () {
      raiz.classList.remove('transicao-revelando', 'transicao-coberta');
      if (depois) depois();
    }, reduzida ? 250 : DURACAO_REVELAR + 180);
  }

  window.quimativaTransicao = { cobrir: cobrir, revelar: revelar };
})();
