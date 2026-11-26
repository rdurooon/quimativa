from backend.api.janela import JanelaAPI
from backend.api.questoes import QuestoesAPI


class API(JanelaAPI, QuestoesAPI):
    """Classe exposta ao JavaScript (pywebview.api.*).

    Cada módulo da bridge é combinado aqui como uma classe mixin.
    """

    def ping(self):
        return 'pong'

    def sair(self):
        import webview  # importado aqui para os testes não dependerem da janela

        for janela in list(webview.windows):
            janela.destroy()
