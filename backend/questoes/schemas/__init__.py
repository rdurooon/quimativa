"""Schemas Pydantic dos payloads dos minijogos.

Uso:
    from backend.questoes.schemas import validar_payload
    payload = validar_payload('identification', dados)  # ValidationError se inválido
"""
from typing import Any

from backend.questoes.schemas.base import PayloadBase
from backend.questoes.schemas.identificacao import IdentificationPayload
from backend.questoes.tipos import MinigameType

# Minijogo -> schema do payload. Os demais entram após a revisão deste padrão.
SCHEMAS_PAYLOAD: dict[MinigameType, type[PayloadBase]] = {
    MinigameType.IDENTIFICATION: IdentificationPayload,
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


__all__ = ['IdentificationPayload', 'PayloadBase', 'PayloadNaoSuportado',
           'SCHEMAS_PAYLOAD', 'obter_schema', 'validar_payload']
