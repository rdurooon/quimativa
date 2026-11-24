"""Leitura e gravação dos metadados do aplicativo (tabela app_metadata)."""
from sqlalchemy.orm import Session

from backend.database.models import AppMetadata

CHAVE_VERSAO_BASE = 'base_content_version'


def obter_metadado(sessao: Session, chave: str, padrao: str | None = None) -> str | None:
    registro = sessao.get(AppMetadata, chave)
    return registro.value if registro else padrao


def definir_metadado(sessao: Session, chave: str, valor: str) -> None:
    registro = sessao.get(AppMetadata, chave)
    if registro is None:
        sessao.add(AppMetadata(key=chave, value=valor))
    else:
        registro.value = valor


def obter_versao_base(sessao: Session) -> int | None:
    """Versão do pacote de questões-base instalado (None = nunca instalado)."""
    valor = obter_metadado(sessao, CHAVE_VERSAO_BASE)
    return int(valor) if valor is not None else None


def definir_versao_base(sessao: Session, versao: int) -> None:
    definir_metadado(sessao, CHAVE_VERSAO_BASE, str(versao))
