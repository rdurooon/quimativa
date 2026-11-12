import os

import webview

from api import API
from config import FRONTEND_DIR, NOME_APP

LARGURA = 1280
ALTURA = 720
DEBUG = os.environ.get('QUIMATIVA_DEBUG') == '1'


def main():
    api = API()
    webview.create_window(
        NOME_APP,
        url=str(FRONTEND_DIR / 'home.html'),
        js_api=api,
        width=LARGURA,
        height=ALTURA,
        min_size=(1024, 600),
    )
    # http_server=True serve o frontend por HTTP local (em vez de file://),
    # o que evita problemas com CSS/JS e é necessário para o Vue + Vite
    webview.start(http_server=True, debug=DEBUG)


if __name__ == '__main__':
    main()