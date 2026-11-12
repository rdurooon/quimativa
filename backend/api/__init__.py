class API:
    """Classe exposta ao JavaScript (pywebview.api.*).

    Cada assunto fica em um mÃ³dulo prÃ³prio (partida.py, equipes.py, ...) como
    uma classe mixin, e Ã© combinado aqui:

        class API(PartidaAPI, EquipesAPI, QuestoesAPI, MinijogosAPI): ...
    """

    def ping(self):
        return 'pong'