from types import SimpleNamespace

from backend import app
from backend.app import calcular_centro


def test_calcular_centro_da_tela_principal():
    telas = [
        SimpleNamespace(x=0, y=0, width=1920, height=1080),
        SimpleNamespace(x=-1920, y=0, width=1920, height=1080),
    ]

    x, y, largura, altura = calcular_centro(telas, 1280, 720)

    assert (x, y, largura, altura) == (320, 180, 1280, 720)


def test_calcular_centro_reduz_janela_maior_que_a_tela():
    telas = [SimpleNamespace(x=0, y=0, width=800, height=600)]

    x, y, largura, altura = calcular_centro(telas, 1280, 720)

    assert (x, y, largura, altura) == (0, 0, 800, 600)


def test_pagina_inicial_de_desenvolvimento_aponta_para_home():
    assert app.obter_pagina_inicial(True) == 'http://127.0.0.1:5173/home.html'


def test_pagina_inicial_de_producao_usa_frontend_absoluto(monkeypatch, tmp_path):
    frontend = tmp_path / 'frontend'
    pagina = frontend / 'dist' / 'home.html'
    pagina.parent.mkdir(parents=True)
    pagina.write_text('<!doctype html>', encoding='utf-8')
    monkeypatch.setattr(app.config, 'FRONTEND_DIR', frontend)

    assert app.obter_pagina_inicial(False) == pagina.as_uri()


def test_pagina_inicial_de_producao_nao_depende_do_diretorio_atual(
    monkeypatch, tmp_path
):
    frontend = tmp_path / 'frontend'
    pagina = frontend / 'dist' / 'home.html'
    pagina.parent.mkdir(parents=True)
    pagina.write_text('<!doctype html>', encoding='utf-8')
    monkeypatch.setattr(app.config, 'FRONTEND_DIR', frontend)
    monkeypatch.chdir(tmp_path.parent)

    assert app.obter_pagina_inicial(False) == pagina.as_uri()


def test_janela_nativa_nao_configura_arraste_personalizado(monkeypatch):
    chamadas = {}

    class Eventos:
        shown = None

    class Janela:
        events = Eventos()

    monkeypatch.setattr(app, 'inicializar_banco', lambda: None)
    monkeypatch.setattr(app, 'carregar_questoes_base', lambda: None)
    monkeypatch.setattr(app, 'ler_tela_cheia', lambda: True)
    monkeypatch.setattr(app, 'fechar_conexoes', lambda: None)
    monkeypatch.setattr(app.webview, 'screens', [])
    monkeypatch.setattr(app.webview, 'create_window',
                        lambda **kwargs: chamadas.update(kwargs) or Janela())
    monkeypatch.setattr(app.webview, 'start', lambda: None)
    monkeypatch.setenv('QUIMATIVA_DEV', '1')

    app.main()

    assert 'frameless' not in chamadas
    assert 'easy_drag' not in chamadas
    assert 'draggable' not in chamadas
    assert chamadas['fullscreen'] is True
    assert chamadas['js_api'].janela_estado() == {'tela_cheia': True}
