"""Arquivos (imagens, estruturas) usados pelas questões.

Os arquivos ficam no disco; aqui guardamos só a referência.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, novo_id

if TYPE_CHECKING:
    from backend.database.models.questao import Question


class QuestionAsset(Base):
    __tablename__ = 'question_assets'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('questions.id', ondelete='CASCADE'), index=True
    )
    file_path: Mapped[str] = mapped_column(String(500))  # caminho RELATIVO à pasta de assets
    asset_type: Mapped[str] = mapped_column(String(30))  # imagem, diagrama...
    role: Mapped[str | None] = mapped_column(String(30))  # molécula principal, alternativa...
    checksum: Mapped[str | None] = mapped_column(String(128))

    question: Mapped[Question] = relationship(back_populates='assets')
