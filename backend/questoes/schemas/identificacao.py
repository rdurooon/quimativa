"""Minijogo 1 — Identificação de função orgânica.

Uma molécula com uma região/grupo destacado e exatamente quatro alternativas
de funções orgânicas, com uma única resposta correta.

Exemplo:
    {
      "molecule_asset_id": "asset-001",
      "highlight": {"region_id": "group-01"},
      "alternatives": [
        {"id": "A", "label": "Álcool"},
        {"id": "B", "label": "Cetona"},
        {"id": "C", "label": "Éster"},
        {"id": "D", "label": "Aldeído"}
      ],
      "correct_alternative_id": "A"
    }

Validado aqui: estrutura, 4 alternativas, IDs e textos sem repetição e
resposta correta existente entre as alternativas.
Validado no serviço (precisa do banco/disco): se o asset da molécula existe.
"""
from typing import Annotated

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Alternativa,
    Esquema,
    Identificador,
    PayloadBase,
    normalizar,
    repetidos,
)

QTD_ALTERNATIVAS = 4


class Destaque(Esquema):
    """Região/grupo funcional destacado na molécula."""

    region_id: Identificador


class IdentificationPayload(PayloadBase):
    molecule_asset_id: Identificador
    highlight: Destaque
    alternatives: Annotated[
        list[Alternativa], Field(min_length=QTD_ALTERNATIVAS, max_length=QTD_ALTERNATIVAS)
    ]
    correct_alternative_id: Identificador

    @model_validator(mode='after')
    def _validar_alternativas(self):
        ids = [a.id for a in self.alternatives]
        if duplicados := repetidos(ids):
            raise ValueError(f'IDs de alternativa repetidos: {", ".join(duplicados)}')

        # Duas alternativas com o mesmo texto tornariam a questão ambígua.
        if duplicados := repetidos(normalizar(a.label) for a in self.alternatives):
            raise ValueError(f'Alternativas com o mesmo texto: {", ".join(duplicados)}')

        if self.correct_alternative_id not in ids:
            raise ValueError(
                f'A resposta correta "{self.correct_alternative_id}" não está entre as alternativas'
            )
        return self
