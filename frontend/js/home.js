(function () {
  var CHAVE_INTRO = 'quimativa.intro-exibida';
  var tela = document.getElementById('home');
  var ultimaMarca = document.querySelector('.m2'); // último elemento a terminar a animação
  var revelada = false;

  // Mostra os demais elementos da tela inicial (INICIAR, Sair, logotipo, rodapé)
  function revelar() {
    if (revelada) return;
    revelada = true;
    tela.classList.add('revelado');
    document.getElementById('btn-iniciar').tabIndex = 0;
    document.getElementById('btn-sair').tabIndex = 0;
    try {
      sessionStorage.setItem(CHAVE_INTRO, '1');
    } catch (e) {}
  }

  // A animação só roda na primeira vez; ao voltar do menu a tela já aparece pronta
  var jaExibida = false;
  try {
    jaExibida = sessionStorage.getItem(CHAVE_INTRO) === '1';
  } catch (e) {}

  if (jaExibida) {
    tela.classList.add('parada');
    revelar();
  } else {
    ultimaMarca.addEventListener('animationend', revelar);
    setTimeout(revelar, 4000); // segurança, caso o evento de fim não dispare
  }

  document.getElementById('btn-iniciar').addEventListener('click', function () {
    // TODO: apontar para o menu principal real quando ele existir
    window.location.href = 'pages/menu.html';
  });

  document.getElementById('btn-sair').addEventListener('click', function () {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.sair) {
      window.pywebview.api.sair();
    } else {
      window.close(); // fallback fora do pywebview (ex.: abrindo no navegador)
    }
  });
})();