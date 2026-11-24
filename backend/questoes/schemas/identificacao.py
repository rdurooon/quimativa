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

Validado no serviço (precisa do banco/disco): se o asset da molécula existe.
"""
from typing import Annotated

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Alternativa,
    Destaque,
    Identificador,
    PayloadBase,
    validar_alternativas,
)

QTD_ALTERNATIVAS = 4


class IdentificationPayload(PayloadBase):
    molecule_asset_id: Identificador
    highlight: Destaque
    alternatives: Annotated[
        list[Alternativa], Field(min_length=QTD_ALTERNATIVAS, max_length=QTD_ALTERNATIVAS)
    ]
    correct_alternative_id: Identificador

    def assets_referenciados(self) -> set[str]:
        return {self.molecule_asset_id}

    def regioes_referenciadas(self) -> dict[str, set[str]]:
        return {self.molecule_asset_id: {self.highlight.region_id}}

    @model_validator(mode='after')
    def _validar(self):
        validar_alternativas(self.alternatives, self.correct_alternative_id)
        return self
