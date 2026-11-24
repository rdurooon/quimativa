"""Minijogo 6 — Ordem das funções.

Quatro funções numa ordem pedida e quatro moléculas numeradas. A equipe
escolhe as moléculas uma por vez; correct_order[i] é a molécula que
corresponde a requested_order[i]. (A avaliação passo a passo fica em game/.)

Exemplo aprovado (Álcool -> Éster -> Amida -> Amina; resposta 1 -> 4 -> 3 -> 2):
    {
      "requested_order": ["Álcool", "Éster", "Amida", "Amina"],
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
    TextoCurto,
    normalizar,
    repetidos,
    validar_moleculas,
)

QTD = 4


class FunctionOrderPayload(PayloadBase):
    requested_order: Annotated[list[TextoCurto], Field(min_length=QTD, max_length=QTD)]
    molecules: Annotated[list[MoleculaRef], Field(min_length=QTD, max_length=QTD)]
    correct_order: Annotated[list[Identificador], Field(min_length=QTD, max_length=QTD)]

    def assets_referenciados(self) -> set[str]:
        return {m.asset_id for m in self.molecules}

    @model_validator(mode='after')
    def _validar(self):
        if duplicados := repetidos(normalizar(f) for f in self.requested_order):
            raise ValueError(f'Funções repetidas na ordem pedida: {", ".join(duplicados)}')

        validar_moleculas(self.molecules)

        ids = [m.id for m in self.molecules]
        if sorted(self.correct_order) != sorted(ids):
            raise ValueError('A sequência correta deve conter cada molécula exatamente uma vez')
        return self
