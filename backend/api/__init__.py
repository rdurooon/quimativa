from backend.api.questoes import QuestoesAPI


class API(QuestoesAPI):
    """Classe exposta ao JavaScript (pywebview.api.*).

    Cada assunto fica em um módulo próprio (questoes.py, partida.py, equipes.py, ...)
    como uma classe mixin, e é combinado aqui:

        class API(QuestoesAPI, PartidaAPI, EquipesAPI, MinijogosAPI): ...
    """

    def ping(self):
        return 'pong'

    def sair(self):
        import webview  # importado aqui para os testes não dependerem da janela

        for janela in list(webview.windows):
            janela.destroy()
