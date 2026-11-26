"""Ponto de entrada do Quimativa.

Executar a partir da raiz do projeto:
    python -m backend.app
"""

import logging
import os
import sys
from pathlib import Path

# Permite também "python backend/app.py" (e o PyInstaller), que não
# colocam a raiz do projeto no caminho de importação.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import webview  # noqa: E402

from backend import config  # noqa: E402
from backend.api import API  # noqa: E402
from backend.api.janela import ler_tela_cheia  # noqa: E402
from backend.database.conexao import fechar_conexoes  # noqa: E402
from backend.database.inicializacao import inicializar_banco  # noqa: E402
from backend.questoes.erros import ErroPacoteBase  # noqa: E402
from backend.questoes.importador import importar_pacote_base  # noqa: E402

log = logging.getLogger("quimativa")


def carregar_questoes_base() -> None:
    """Importa o pacote oficial. Um pacote com erro não impede o app de abrir."""
    try:
        importar_pacote_base()
    except ErroPacoteBase as erro:
        log.error("%s", erro)
    except Exception:
        log.exception("Falha inesperada ao importar as questões-base")


def calcular_centro(telas, largura_janela: int, altura_janela: int):
    tela_principal = next(
        (tela for tela in telas if tela.x == 0 and tela.y == 0),
        telas[0] if telas else None,
    )
    if tela_principal is None:
        return None, None, largura_janela, altura_janela

    largura_tela = max(1, int(tela_principal.width))
    altura_tela = max(1, int(tela_principal.height))
    largura_util = min(largura_janela, largura_tela)
    altura_util = min(altura_janela, altura_tela)
    x = int(tela_principal.x + (largura_tela - largura_util) // 2)
    y = int(tela_principal.y + (altura_tela - altura_util) // 2)
    return x, y, largura_util, altura_util


def obter_pagina_inicial(modo_desenvolvimento: bool) -> str:
    if modo_desenvolvimento:
        return "http://127.0.0.1:5173/home.html"

    pagina_inicial = config.FRONTEND_DIR / "dist" / "home.html"
    if not pagina_inicial.is_file():
        raise FileNotFoundError(
            f"Frontend compilado não encontrado em {pagina_inicial}. "
            'Execute "npm run build" em frontend.'
        )
    return pagina_inicial.as_uri()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s"
    )

    inicializar_banco()
    carregar_questoes_base()

    modo_desenvolvimento = os.environ.get("QUIMATIVA_DEV", "").lower() in {
        "1",
        "true",
        "yes",
    }
    pagina_inicial = obter_pagina_inicial(modo_desenvolvimento)

    largura_janela = 1280
    altura_janela = 720

    x, y, largura_util, altura_util = calcular_centro(
        webview.screens,
        largura_janela,
        altura_janela,
    )

    tela_cheia = ler_tela_cheia()
    api = API(tela_cheia=tela_cheia)
    janela = webview.create_window(
        title=config.NOME_APP,
        url=pagina_inicial,
        js_api=api,
        x=x,
        y=y,
        width=largura_util,
        height=altura_util,
        resizable=False,
        fullscreen=tela_cheia,
    )
    api._vincular_janela(janela)

    try:
        webview.start()
    finally:
        fechar_conexoes()


if __name__ == "__main__":
    main()
