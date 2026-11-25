"""Dados gerais de uma questão (entrada de criação/edição e pacote base).

O `payload` chega aqui como dicionário e é validado à parte pelo schema do
minijogo (ver validar_payload), para que os erros apontem o campo exato.
"""
from typing import Annotated, Any

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Esquema,
    Identificador,
    TextoCurto,
    TextoLongo,
    normalizar,
    repetidos,
)
from backend.questoes.tipos import Difficulty, MinigameType

MAX_TAGS = 20


class FonteEntrada(Esquema):
    """Origem de uma questão externa (prova, livro...) e suas adaptações."""

    name: TextoCurto                    # ex.: "ENEM 2023"
    reference: TextoLongo | None = None  # link, edição, questão nº...
    license: TextoCurto | None = None
    notes: TextoLongo | None = None      # descrição das adaptações feitas


class DadosQuestao(Esquema):
    minigame_type: MinigameType
    difficulty: Difficulty
    statement: TextoLongo
    payload: dict[str, Any]
    package_id: Identificador | None = None
    explanation: TextoLongo | None = None
    tags: Annotated[list[TextoCurto], Field(max_length=MAX_TAGS)] = []
    source: FonteEntrada | None = None

    @model_validator(mode='after')
    def _tags_sem_repeticao(self):
        if duplicadas := repetidos(normalizar(t) for t in self.tags):
            raise ValueError(f'Tags repetidas: {", ".join(duplicadas)}')
        return self
