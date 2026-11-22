"""Fontes de questões externas (prova, instituição, material) e adaptações."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, novo_id

if TYPE_CHECKING:
    from backend.database.models.questao import Question


class QuestionSource(Base):
    __tablename__ = 'question_sources'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    name: Mapped[str] = mapped_column(String(200))
    reference: Mapped[str | None] = mapped_column(Text)  # link, edição, ano...
    license: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)

    # passive_deletes='all': o banco impede excluir uma fonte ainda usada por questões
    questions: Mapped[list[Question]] = relationship(back_populates='source', passive_deletes='all')
