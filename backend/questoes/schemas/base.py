"""Peças comuns aos schemas de payload dos minijogos."""
from collections.abc import Iterable
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


class Alternativa(Esquema):
    id: Identificador
    label: TextoCurto


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
