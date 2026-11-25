"""Minijogo 6 — Ordem das funções.

O enunciado instrui o jogador sobre a sequência. ``correct_order`` guarda
os IDs na ordem exata em que o criador marcou as quatro moléculas.

Exemplo aprovado (Álcool -> Éster -> Amida -> Amina; resposta 1 -> 4 -> 3 -> 2):
    {
      "molecules": [
        {"id": "M1", "asset_id": "asset-009"},
        {"id": "M2", "asset_id": "asset-010"},
        {"id": "M3", "asset_id": "asset-011"},
        {"id": "M4", "asset_id": "asset-012"}
      ],
      "correct_order": ["M1", "M4", "M3", "M2"]
    }
"""
from typing import Annotated

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Identificador,
    MoleculaRef,
    PayloadBase,
    validar_moleculas,
)

QTD = 4


class FunctionOrderPayload(PayloadBase):
    molecules: Annotated[list[MoleculaRef], Field(min_length=QTD, max_length=QTD)]
    correct_order: Annotated[list[Identificador], Field(min_length=QTD, max_length=QTD)]

    def assets_referenciados(self) -> set[str]:
        return {m.asset_id for m in self.molecules}

    @model_validator(mode='after')
    def _validar(self):
        validar_moleculas(self.molecules)

        ids = [m.id for m in self.molecules]
        if sorted(self.correct_order) != sorted(ids):
            raise ValueError('A sequência correta deve conter cada molécula exatamente uma vez')
        return self
