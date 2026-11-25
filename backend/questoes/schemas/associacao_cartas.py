"""Minijogo 3 — Associação de cartas.

Exatamente quatro cartas; apenas duas formam o par válido (um único par).
Cada carta tem texto principal ou imagem, além de texto complementar opcional.

Exemplo:
    {
      "cards": [
        {"id": "C1", "asset_id": "asset-010"},
        {"id": "C2", "content": "Álcool"},
        {"id": "C3", "asset_id": "asset-011"},
        {"id": "C4", "content": "Cetona"}
      ],
      "correct_pair": ["C1", "C2"]
    }

LIMITE: o schema bloqueia cartas repetidas, mas não consegue saber se, pela
química, outra combinação também faria sentido (ex.: C3 também ser álcool).
Isso precisa ser garantido na revisão do conteúdo.
"""
from typing import Annotated

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Esquema,
    Identificador,
    PayloadBase,
    TextoCurto,
    normalizar,
    repetidos,
)

QTD_CARTAS = 4


class Carta(Esquema):
    id: Identificador
    content: TextoCurto | None = None
    asset_id: Identificador | None = None
    supplementary_text: TextoCurto | None = None

    @model_validator(mode='after')
    def _validar_conteudo_principal(self):
        if (self.content is None) == (self.asset_id is None):
            raise ValueError(f'A carta "{self.id}" precisa de exatamente um texto principal ou imagem')
        return self


def validar_cartas(cartas: list[Carta]) -> None:
    ids = [c.id for c in cartas]
    if duplicados := repetidos(ids):
        raise ValueError(f'IDs de carta repetidos: {", ".join(duplicados)}')

    textos = [normalizar(c.content) for c in cartas if c.content is not None]
    if duplicados := repetidos(textos):
        raise ValueError(f'Cartas com o mesmo conteúdo: {", ".join(duplicados)}')

    imagens = [c.asset_id for c in cartas if c.asset_id is not None]
    if duplicados := repetidos(imagens):
        raise ValueError(f'A mesma imagem (asset {", ".join(duplicados)}) aparece mais de uma vez')


class CardAssociationPayload(PayloadBase):
    cards: Annotated[list[Carta], Field(min_length=QTD_CARTAS, max_length=QTD_CARTAS)]
    correct_pair: Annotated[list[Identificador], Field(min_length=2, max_length=2)]

    def assets_referenciados(self) -> set[str]:
        return {c.asset_id for c in self.cards if c.asset_id is not None}

    @model_validator(mode='after')
    def _validar(self):
        validar_cartas(self.cards)

        ids = [c.id for c in self.cards]
        primeira, segunda = self.correct_pair
        if primeira == segunda:
            raise ValueError('O par correto precisa ter duas cartas diferentes')
        for carta in self.correct_pair:
            if carta not in ids:
                raise ValueError(f'A carta "{carta}" do par correto não existe')
        return self
