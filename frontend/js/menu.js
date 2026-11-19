(function () {
  var chaveTransicao = 'quimativa.transicao-menu';
  var veioDaHome = false;

  try {
    veioDaHome = sessionStorage.getItem(chaveTransicao) === '1';
    sessionStorage.removeItem(chaveTransicao);
  } catch (e) {}

  if (veioDaHome) {
    document.documentElement.classList.remove('transicao-entrada');
    document.documentElement.classList.add('transicao-coberta');
    window.quimativaTransicao.revelar();
  }

  document.getElementById('btn-sair').addEventListener('click', function () {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.sair) {
      window.pywebview.api.sair();
    } else {
      window.close();
    }
  });
})();
