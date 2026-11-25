"""Minijogo 5 — Qual molécula pertence à função?

Quatro cartas são apresentadas; o enunciado informa a função e uma carta
correta é selecionada.
"""
from typing import Any

from pydantic import Field, model_validator

from backend.questoes.schemas.associacao_cartas import Carta, QTD_CARTAS, validar_cartas
from backend.questoes.schemas.base import Identificador, PayloadBase, TextoCurto


class FunctionMoleculePayload(PayloadBase):
    cards: list[Carta] = Field(min_length=QTD_CARTAS, max_length=QTD_CARTAS)
    correct_card_id: Identificador
    target_function: TextoCurto | None = None

    def assets_referenciados(self) -> set[str]:
        return {card.asset_id for card in self.cards if card.asset_id is not None}

    @model_validator(mode='after')
    def _validar(self):
        validar_cartas(self.cards)
        if self.correct_card_id not in {card.id for card in self.cards}:
            raise ValueError(f'A carta correta "{self.correct_card_id}" não existe')
        return self

    @model_validator(mode='before')
    @classmethod
    def _converter_payload_antigo(cls, dados: Any) -> Any:
        if not isinstance(dados, dict) or 'cards' in dados or 'molecules' not in dados:
            return dados
        molecules = dados['molecules']
        if not isinstance(molecules, list) or any(not isinstance(item, dict) for item in molecules):
            return dados

        convertido = dict(dados)
        convertido['cards'] = [dict(item) for item in molecules]
        convertido['correct_card_id'] = convertido.pop('correct_molecule_id', None)
        convertido.pop('molecules')
        return convertido
