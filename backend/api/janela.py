"""Preferências e comandos da janela nativa."""

import logging
from threading import Lock

from sqlalchemy.exc import SQLAlchemyError

from backend.database.conexao import sessao
from backend.database.metadados import definir_metadado, obter_metadado

CHAVE_TELA_CHEIA = "window_fullscreen"
log = logging.getLogger(__name__)


def ler_tela_cheia() -> bool:
    with sessao() as banco:
        return obter_metadado(banco, CHAVE_TELA_CHEIA) == "1"


class JanelaAPI:
    def __init__(self, tela_cheia: bool = False):
        self._tela_cheia = tela_cheia
        self._janela = None
        self._trava_janela = Lock()

    def _vincular_janela(self, janela):
        self._janela = janela

    def janela_estado(self):
        with self._trava_janela:
            return {"tela_cheia": self._tela_cheia}

    def janela_alternar_tela_cheia(self):
        with self._trava_janela:
            if self._janela is None:
                raise RuntimeError("A janela principal ainda não foi iniciada.")

            # No Windows o PyWebView usa o monitor que contém a janela.
            self._janela.toggle_fullscreen()
            self._tela_cheia = not self._tela_cheia
            salva = True
            try:
                with sessao() as banco:
                    definir_metadado(banco, CHAVE_TELA_CHEIA, "1" if self._tela_cheia else "0")
            except SQLAlchemyError:
                log.exception("Falha ao salvar a preferência de tela cheia.")
                salva = False

            return {"tela_cheia": self._tela_cheia, "salva": salva}
