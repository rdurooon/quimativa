"""Testes da validação de SVG."""
import hashlib

import pytest

from backend.questoes.svg import SvgInvalido, validar_caminho_relativo, validar_svg

SVG_OK = (
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 10 10">'
    '<defs><linearGradient id="grad"/></defs>'
    '<g id="grupo-oh"><circle cx="5" cy="5" r="2" fill="url(#grad)"/></g>'
    '<use xlink:href="#grupo-oh"/>'
    '<style>.a { fill: url(#grad); }</style>'
    '</svg>'
)


def test_svg_valido_devolve_ids_e_checksum():
    r = validar_svg(SVG_OK)
    assert r.ids == {'grad', 'grupo-oh'}
    assert r.checksum == hashlib.sha256(SVG_OK.encode()).hexdigest()


@pytest.mark.parametrize('conteudo, mensagem', [
    ('', 'vazio'),
    ('<svg', 'XML inválido'),
    ('<html xmlns="http://www.w3.org/1999/xhtml"/>', 'raiz precisa ser <svg>'),
    ('<!DOCTYPE svg [<!ENTITY x "y">]><svg xmlns="http://www.w3.org/2000/svg"/>', 'DOCTYPE'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', '<script>'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><SCRIPT>x</SCRIPT></svg>', '<script>'),
    ('<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>', 'onload'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><foreignObject/></svg>', 'foreignobject'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><a href="javascript:alert(1)"/></svg>', 'JavaScript'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><image href="http://site.com/x.png"/></svg>', 'Link externo'),
    ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
     '<image xlink:href="data:image/png;base64,AAA"/></svg>', 'Link externo'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="url(http://x.com/a)"/></svg>', 'externa'),
    ('<svg xmlns="http://www.w3.org/2000/svg"><style>@import url(a.css);</style></svg>', 'externa'),
])
def test_svg_invalido(conteudo, mensagem):
    with pytest.raises(SvgInvalido, match=mensagem):
        validar_svg(conteudo)


def test_svg_muito_grande():
    grande = '<svg xmlns="http://www.w3.org/2000/svg">' + ' ' * (2 * 1024 * 1024) + '</svg>'
    with pytest.raises(SvgInvalido, match='2 MB'):
        validar_svg(grande)


@pytest.mark.parametrize('caminho, esperado', [
    ('etanol.svg', 'etanol.svg'),
    ('moleculas\\etanol.svg', 'moleculas/etanol.svg'),
    (' alcool/metanol.SVG ', 'alcool/metanol.SVG'),
])
def test_caminho_relativo_valido(caminho, esperado):
    assert validar_caminho_relativo(caminho) == esperado


@pytest.mark.parametrize('caminho', [
    '', '/etc/x.svg', 'C:/x.svg', '../fora.svg', 'a/../b.svg', 'a//b.svg', 'etanol.png',
])
def test_caminho_relativo_invalido(caminho):
    with pytest.raises(SvgInvalido):
        validar_caminho_relativo(caminho)
