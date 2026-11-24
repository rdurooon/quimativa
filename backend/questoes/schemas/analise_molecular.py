"""Minijogo 4 — Análise molecular.

Uma molécula e uma pergunta de interpretação com alternativas (contagem de
carbonos, cadeia aberta/fechada, saturação, grupos funcionais, região
destacada...). Não se limita a identificar a função orgânica.

PENDENTE (documento mestre): formato exato. Por isso a quantidade de
alternativas só exige o mínimo (2) e o destaque de região é opcional.

Exemplo:
    {
      "molecule_asset_id": "asset-005",
      "question": "Qual é a classificação da cadeia carbônica?",
      "alternatives": [
        {"id": "A", "label": "Aberta"},
        {"id": "B", "label": "Fechada"},
        {"id": "C", "label": "Mista"},
        {"id": "D", "label": "Aromática"}
      ],
      "correct_alternative_id": "A"
    }
"""
from typing import Annotated

from pydantic import Field, model_validator

from backend.questoes.schemas.base import (
    Alternativa,
    Destaque,
    Identificador,
    PayloadBase,
    TextoLongo,
    validar_alternativas,
)

MIN_ALTERNATIVAS = 2


class MolecularAnalysisPayload(PayloadBase):
    molecule_asset_id: Identificador
    question: TextoLongo
    highlight: Destaque | None = None
    alternatives: Annotated[list[Alternativa], Field(min_length=MIN_ALTERNATIVAS)]
    correct_alternative_id: Identificador

    def assets_referenciados(self) -> set[str]:
        return {self.molecule_asset_id}

    def regioes_referenciadas(self) -> dict[str, set[str]]:
        if self.highlight is None:
            return {}
        return {self.molecule_asset_id: {self.highlight.region_id}}

    @model_validator(mode='after')
    def _validar(self):
        validar_alternativas(self.alternatives, self.correct_alternative_id)
        return self
