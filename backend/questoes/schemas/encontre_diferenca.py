"""Minijogo 2 — Encontre a diferença.

Duas moléculas; o enunciado descreve o critério e há uma resposta correta.

Exemplo:
    {
      "molecules": [
        {"id": "M1", "asset_id": "asset-002"},
        {"id": "M2", "asset_id": "asset-003"},
        {"id": "M3", "asset_id": "asset-004"}
      ],
      "criterion": "Possui função éster",
      "correct_molecule_id": "M2"
    }
"""
from typing import Annotated

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Identificador,
    MoleculaRef,
    PayloadBase,
    TextoCurto,
    validar_moleculas,
)

QTD_MOLECULAS = 2


class FindDifferencePayload(PayloadBase):
    molecules: Annotated[list[MoleculaRef], Field(min_length=QTD_MOLECULAS, max_length=QTD_MOLECULAS)]
    # Compatibilidade com payloads antigos; novos formulários usam statement.
    criterion: TextoCurto | None = None
    correct_molecule_id: Identificador

    def assets_referenciados(self) -> set[str]:
        return {m.asset_id for m in self.molecules}

    @model_validator(mode='after')
    def _validar(self):
        validar_moleculas(self.molecules, self.correct_molecule_id)
        return self
