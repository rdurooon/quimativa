"""Arquivos SVG (estruturas moleculares) reaproveitáveis entre questões.

O arquivo fica no disco, na pasta de assets da origem (ver config.obter_assets_dir);
aqui guardamos só a referência. Um mesmo asset pode ser usado por várias questões.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, agora_utc, novo_id
from backend.questoes.tipos import AssetType, SourceType

if TYPE_CHECKING:
    from backend.database.models.questao_asset import QuestionAsset


def _valores_sql(enum) -> str:
    return ', '.join(f"'{item.value}'" for item in enum)


class Asset(Base):
    __tablename__ = 'assets'
    __table_args__ = (
        CheckConstraint(f'asset_type IN ({_valores_sql(AssetType)})', name='asset_type_valido'),
        CheckConstraint(f'source_type IN ({_valores_sql(SourceType)})', name='source_type_valido'),
        # o mesmo arquivo não pode ser registrado duas vezes na mesma origem
        UniqueConstraint('source_type', 'file_path'),
    )

    # Base: ID fixo vindo do pacote oficial. Local: UUID gerado.
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=novo_id)
    source_type: Mapped[str] = mapped_column(String(10), index=True)
    file_path: Mapped[str] = mapped_column(String(500))  # RELATIVO à pasta de assets da origem
    asset_type: Mapped[str] = mapped_column(String(30), default=AssetType.SVG)
    name: Mapped[str | None] = mapped_column(String(200))  # nome amigável (ex.: "Etanol")
    checksum: Mapped[str | None] = mapped_column(String(128))  # SHA-256 do arquivo
    created_at: Mapped[datetime] = mapped_column(DateTime, default=agora_utc)

    # passive_deletes='all': o banco impede excluir um asset ainda usado por questões
    question_links: Mapped[list[QuestionAsset]] = relationship(
        back_populates='asset', passive_deletes='all'
    )

    def __repr__(self) -> str:
        return f'<Asset {self.id} {self.source_type} {self.file_path}>'
