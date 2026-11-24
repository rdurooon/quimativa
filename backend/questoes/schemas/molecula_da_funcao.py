"""Minijogo 5 — Qual molécula pertence à função?

Apresenta uma função orgânica e duas ou mais moléculas; a equipe escolhe a
molécula que apresenta a função. Uma resposta correta.
(Inverso do minijogo 1: aqui a função é dada e a molécula é escolhida.)

Exemplo:
    {
      "target_function": "Éster",
      "molecules": [
        {"id": "M1", "asset_id": "asset-006"},
        {"id": "M2", "asset_id": "asset-007"},
        {"id": "M3", "asset_id": "asset-008"}
      ],
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


class FunctionMoleculePayload(PayloadBase):
    target_function: TextoCurto
    molecules: Annotated[list[MoleculaRef], Field(min_length=MIN_MOLECULAS)]
    correct_molecule_id: Identificador

    def assets_referenciados(self) -> set[str]:
        return {m.asset_id for m in self.molecules}

    @model_validator(mode='after')
    def _validar(self):
        validar_moleculas(self.molecules, self.correct_molecule_id)
        return self
