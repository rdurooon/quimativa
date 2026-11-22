"""Assuntos/classificações das questões (Álcool, Cadeia aberta...)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, novo_id

if TYPE_CHECKING:
    from backend.database.models.questao import Question


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    questions: Mapped[list[Question]] = relationship(secondary='question_tags', back_populates='tags')
