"""Schemas Pydantic dos payloads dos minijogos.

Uso:
    from backend.questoes.schemas import validar_payload
    payload = validar_payload('identification', dados)  # ValidationError se inválido
"""
from typing import Any

from backend.questoes.schemas.analise_molecular import MolecularAnalysisPayload
from backend.questoes.schemas.associacao_cartas import CardAssociationPayload
from backend.questoes.schemas.base import PayloadBase
from backend.questoes.schemas.encontre_diferenca import FindDifferencePayload
from backend.questoes.schemas.identificacao import IdentificationPayload
from backend.questoes.schemas.molecula_da_funcao import FunctionMoleculePayload
from backend.questoes.schemas.ordem_funcoes import FunctionOrderPayload
from backend.questoes.tipos import MinigameType

# Minijogo -> schema do payload.
SCHEMAS_PAYLOAD: dict[MinigameType, type[PayloadBase]] = {
    MinigameType.IDENTIFICATION: IdentificationPayload,
    MinigameType.FIND_DIFFERENCE: FindDifferencePayload,
    MinigameType.CARD_ASSOCIATION: CardAssociationPayload,
    MinigameType.MOLECULAR_ANALYSIS: MolecularAnalysisPayload,
    MinigameType.FUNCTION_MOLECULE: FunctionMoleculePayload,
    MinigameType.FUNCTION_ORDER: FunctionOrderPayload,
}


class PayloadNaoSuportado(ValueError):
    """O minijogo existe, mas ainda não tem schema implementado."""


def obter_schema(minigame_type: str) -> type[PayloadBase]:
    tipo = MinigameType(minigame_type)  # ValueError se o minijogo não existir
    try:
        return SCHEMAS_PAYLOAD[tipo]
    except KeyError:
        raise PayloadNaoSuportado(f'Minijogo "{tipo.value}" ainda não possui schema de payload') from None


def validar_payload(minigame_type: str, payload: dict[str, Any]) -> PayloadBase:
    """Valida o payload com o schema do minijogo e devolve o objeto validado."""
    return obter_schema(minigame_type).model_validate(payload)


__all__ = [
    'CardAssociationPayload', 'FindDifferencePayload', 'FunctionMoleculePayload',
    'FunctionOrderPayload', 'IdentificationPayload', 'MolecularAnalysisPayload',
    'PayloadBase', 'PayloadNaoSuportado', 'SCHEMAS_PAYLOAD', 'obter_schema', 'validar_payload',
]
