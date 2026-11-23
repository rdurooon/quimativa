from types import SimpleNamespace

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
