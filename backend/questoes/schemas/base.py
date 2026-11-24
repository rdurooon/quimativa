"""Peças comuns aos schemas de payload dos minijogos."""
from collections.abc import Iterable, Sequence
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

# Texto obrigatório: espaços nas pontas são removidos e não pode ficar vazio.
Identificador = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
TextoCurto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TextoLongo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class Esquema(BaseModel):
    """Base de todos os schemas: rejeita campos desconhecidos."""

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class PayloadBase(Esquema):
    """Base dos payloads (campo JSON `payload` da tabela questions)."""

    def assets_referenciados(self) -> set[str]:
        """IDs dos assets (SVGs) usados pelo payload. Cada minijogo sobrescreve."""
        return set()

    def regioes_referenciadas(self) -> dict[str, set[str]]:
        """{asset_id: {ids de regiões destacadas}} que precisam existir no SVG."""
        return {}


class Alternativa(Esquema):
    id: Identificador
    label: TextoCurto


class Destaque(Esquema):
    """Região/grupo funcional destacado na molécula."""

    region_id: Identificador


class MoleculaRef(Esquema):
    """Molécula apresentada como opção, referenciando sua imagem (asset)."""

    id: Identificador
    asset_id: Identificador


# --- Funções auxiliares -----------------------------------------------------

def normalizar(texto: str) -> str:
    """Forma usada para comparar textos: sem diferença de maiúsculas/espaços."""
    return ' '.join(texto.split()).casefold()


def repetidos(valores: Iterable[str]) -> list[str]:
    """Valores que aparecem mais de uma vez (na ordem em que aparecem)."""
    vistos, duplicados = set(), []
    for valor in valores:
        if valor in vistos and valor not in duplicados:
            duplicados.append(valor)
        vistos.add(valor)
    return duplicados


def validar_alternativas(alternativas: Sequence[Alternativa], correta: str) -> None:
    """IDs únicos, textos sem repetição (evita ambiguidade) e resposta existente."""
    ids = [a.id for a in alternativas]
    if duplicados := repetidos(ids):
        raise ValueError(f'IDs de alternativa repetidos: {", ".join(duplicados)}')
    if duplicados := repetidos(normalizar(a.label) for a in alternativas):
        raise ValueError(f'Alternativas com o mesmo texto: {", ".join(duplicados)}')
    if correta not in ids:
        raise ValueError(f'A resposta correta "{correta}" não está entre as alternativas')


def validar_moleculas(moleculas: Sequence[MoleculaRef], correta: str | None = None) -> None:
    """IDs únicos, sem a mesma imagem repetida e (se informada) molécula correta existente."""
    ids = [m.id for m in moleculas]
    if duplicados := repetidos(ids):
        raise ValueError(f'IDs de molécula repetidos: {", ".join(duplicados)}')
    if duplicados := repetidos(m.asset_id for m in moleculas):
        raise ValueError(f'A mesma molécula (asset {", ".join(duplicados)}) aparece mais de uma vez')
    if correta is not None and correta not in ids:
        raise ValueError(f'A molécula correta "{correta}" não está entre as moléculas')
