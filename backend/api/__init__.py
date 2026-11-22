import webview


class API:
    """Classe exposta ao JavaScript (pywebview.api.*).

    Cada assunto fica em um módulo próprio (partida.py, equipes.py, ...) como
    uma classe mixin, e é combinado aqui:

        class API(PartidaAPI, EquipesAPI, QuestoesAPI, MinijogosAPI): ...
    """

    def ping(self):
        return 'pong'

    def sair(self):
        for janela in list(webview.windows):
            janela.destroy()
