"""Minijogo 2 — Encontre a diferença.

Duas ou mais moléculas; a equipe escolhe a que possui a característica pedida
(critério explícito: função, ramificação, saturação...). Uma resposta correta.

PENDENTE (documento mestre): quantidade exata de moléculas e tipos de
comparação. Por isso só o mínimo (2) é exigido, sem máximo.

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

MIN_MOLECULAS = 2


class FindDifferencePayload(PayloadBase):
    molecules: Annotated[list[MoleculaRef], Field(min_length=MIN_MOLECULAS)]
    criterion: TextoCurto
    correct_molecule_id: Identificador

    def assets_referenciados(self) -> set[str]:
        return {m.asset_id for m in self.molecules}

    @model_validator(mode='after')
    def _validar(self):
        validar_moleculas(self.molecules, self.correct_molecule_id)
        return self
