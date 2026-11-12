window.addEventListener('pywebviewready', function () {
  document.getElementById('btn-teste').addEventListener('click', async function () {
    var resposta = await pywebview.api.ping();
    document.getElementById('resposta').textContent = 'Python respondeu: ' + resposta;
  });
});