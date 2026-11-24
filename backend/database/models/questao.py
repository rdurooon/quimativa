"""Tabela principal de questões e a ligação questões <-> tags."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, agora_utc, novo_id
from backend.questoes.tipos import Difficulty, MinigameType, SourceType

if TYPE_CHECKING:
    from backend.database.models.fonte_questao import QuestionSource
    from backend.database.models.questao_asset import QuestionAsset
    from backend.database.models.tag import Tag


def _valores_sql(enum) -> str:
    return ', '.join(f"'{item.value}'" for item in enum)


question_tags = Table(
    'question_tags',
    Base.metadata,
    Column('question_id', String(36), ForeignKey('questions.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', String(36), ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True, index=True),
)


class Question(Base):
    """Uma questão, de qualquer minijogo e de qualquer origem.

    Os dados específicos de cada minijogo ficam em `payload` (JSON) e são
    validados pelos schemas Pydantic em backend/questoes/schemas/.
    Ao editar o payload, atribua um dicionário novo (não altere o existente),
    senão o SQLAlchemy não percebe a mudança.
    """

    __tablename__ = 'questions'
    __table_args__ = (
        CheckConstraint(f'minigame_type IN ({_valores_sql(MinigameType)})', name='minigame_type_valido'),
        CheckConstraint(f'difficulty BETWEEN {min(Difficulty)} AND {max(Difficulty)}', name='difficulty_valida'),
        CheckConstraint(f'source_type IN ({_valores_sql(SourceType)})', name='source_type_valido'),
        # remote_id só existe (e é obrigatório) em questões remotas
        CheckConstraint("(source_type = 'remote') = (remote_id IS NOT NULL)", name='remote_id_somente_remotas'),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    minigame_type: Mapped[str] = mapped_column(String(30), index=True)
    difficulty: Mapped[int] = mapped_column(index=True)
    source_type: Mapped[str] = mapped_column(String(10), index=True)
    statement: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    explanation: Mapped[str | None] = mapped_column(Text)
    source_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey('question_sources.id', ondelete='RESTRICT')
    )
    status: Mapped[str | None] = mapped_column(String(30))  # fluxo editorial ainda não definido
    remote_id: Mapped[str | None] = mapped_column(String(100), index=True, unique=True)
    remote_version: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=agora_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=agora_utc, onupdate=agora_utc)

    asset_links: Mapped[list[QuestionAsset]] = relationship(
        back_populates='question', cascade='all, delete-orphan', passive_deletes=True
    )
    tags: Mapped[list[Tag]] = relationship(secondary=question_tags, back_populates='questions')
    source: Mapped[QuestionSource | None] = relationship(back_populates='questions')

    def __repr__(self) -> str:
        return f'<Question {self.id} {self.minigame_type} {self.source_type}>'
