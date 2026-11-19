"""Ponto de entrada do Quimativa.

Executar a partir da raiz do projeto:
    python -m backend.app
"""
import logging
import sys
from pathlib import Path

# Permite também "python backend/app.py" (e o PyInstaller), que não
# colocam a raiz do projeto no caminho de importação.
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import webview  # noqa: E402

from backend import config  # noqa: E402
from backend.api import API  # noqa: E402
from backend.database.conexao import fechar_conexoes  # noqa: E402
from backend.database.inicializacao import inicializar_banco  # noqa: E402


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(name)s] %(message)s')

    inicializar_banco()

    pagina_inicial = config.FRONTEND_DIR / 'home.html'
    webview.create_window(
        title=config.NOME_APP,
        url=pagina_inicial.as_uri(),
        js_api=API(),
        width=1280,
        height=720,
        resizable=False,
    )
    try:
        webview.start()
    finally:
        fechar_conexoes()


if __name__ == '__main__':
    main()
