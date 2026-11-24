"""Validação de arquivos SVG das questões.

Um SVG pode conter código (JavaScript) e links externos. Como o app roda numa
janela com acesso à API do Python, qualquer SVG que entre no banco precisa
ser verificado. Regras:

- precisa ser um XML válido cuja raiz é <svg>;
- sem DOCTYPE/ENTITY (evita ataques de XML);
- sem <script>, <foreignObject>, <iframe>, <embed>, <object>;
- sem atributos de evento (onclick, onload...);
- sem links externos (href e url() só podem apontar para '#id' dentro do próprio arquivo);
- tamanho máximo de 2 MB.

O frontend deve exibir os SVGs com <img src="...">, nunca inserindo o
conteúdo direto na página (v-html).
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

TAMANHO_MAXIMO = 2 * 1024 * 1024  # 2 MB

ELEMENTOS_PROIBIDOS = {'script', 'foreignobject', 'iframe', 'embed', 'object', 'handler', 'listener'}
ATRIBUTOS_LINK = {'href'}

# url(...) que NÃO começa com '#': aponta para fora do arquivo.
URL_EXTERNA = re.compile(r'url\(\s*["\']?\s*(?!#)', re.IGNORECASE)


class SvgInvalido(ValueError):
    """O arquivo não é um SVG aceito pelo Quimativa."""


@dataclass(frozen=True)
class SvgValidado:
    conteudo: bytes
    checksum: str            # SHA-256 em hexadecimal
    ids: frozenset[str]      # ids dos elementos (usados como regiões destacáveis)


def _nome_local(nome: str) -> str:
    """Remove o namespace: '{http://www.w3.org/2000/svg}g' -> 'g'."""
    return nome.rsplit('}', 1)[-1].lower()


def validar_svg(conteudo: bytes | str) -> SvgValidado:
    """Valida o SVG e devolve conteúdo, checksum e ids dos elementos."""
    if isinstance(conteudo, str):
        conteudo = conteudo.encode('utf-8')

    if not conteudo.strip():
        raise SvgInvalido('Arquivo vazio')
    if len(conteudo) > TAMANHO_MAXIMO:
        raise SvgInvalido('Arquivo maior que 2 MB')

    cabecalho = conteudo.upper()
    if b'<!DOCTYPE' in cabecalho or b'<!ENTITY' in cabecalho:
        raise SvgInvalido('SVG com DOCTYPE/ENTITY não é permitido')

    try:
        raiz = ET.fromstring(conteudo)
    except ET.ParseError as erro:
        raise SvgInvalido(f'XML inválido: {erro}') from None

    if _nome_local(raiz.tag) != 'svg':
        raise SvgInvalido('O arquivo não é um SVG (a raiz precisa ser <svg>)')

    ids: set[str] = set()
    for elemento in raiz.iter():
        if not isinstance(elemento.tag, str):
            continue  # comentários / instruções de processamento
        nome = _nome_local(elemento.tag)
        if nome in ELEMENTOS_PROIBIDOS:
            raise SvgInvalido(f'Elemento <{nome}> não é permitido')

        if nome == 'style' and elemento.text:
            if '@import' in elemento.text.lower() or URL_EXTERNA.search(elemento.text):
                raise SvgInvalido('Estilo com referência externa não é permitido')

        for atributo, valor in elemento.attrib.items():
            atributo = _nome_local(atributo)
            valor_limpo = valor.strip().lower()
            if atributo.startswith('on'):
                raise SvgInvalido(f'Atributo de evento "{atributo}" não é permitido')
            if 'javascript:' in valor_limpo.replace(' ', ''):
                raise SvgInvalido('Código JavaScript não é permitido')
            if atributo in ATRIBUTOS_LINK and not valor_limpo.startswith('#'):
                raise SvgInvalido(f'Link externo não é permitido: {valor}')
            if URL_EXTERNA.search(valor):
                raise SvgInvalido(f'Referência externa não é permitida no atributo "{atributo}"')

        if id_elemento := elemento.get('id'):
            ids.add(id_elemento)

    return SvgValidado(
        conteudo=conteudo,
        checksum=hashlib.sha256(conteudo).hexdigest(),
        ids=frozenset(ids),
    )


def validar_caminho_relativo(caminho: str) -> str:
    """Confere se o caminho de um asset é relativo, seguro e termina em .svg.

    Devolve o caminho normalizado com barras '/'.
    """
    normalizado = caminho.strip().replace('\\', '/')
    partes = normalizado.split('/')
    if (
        not normalizado
        or normalizado.startswith('/')
        or ':' in normalizado
        or any(p in ('', '.', '..') for p in partes)
    ):
        raise SvgInvalido(f'Caminho de asset inválido: "{caminho}"')
    if not normalizado.lower().endswith('.svg'):
        raise SvgInvalido(f'O asset precisa ser um arquivo .svg: "{caminho}"')
    return normalizado
