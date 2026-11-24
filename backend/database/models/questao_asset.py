"""Ligação entre questões e assets (muitos-para-muitos).

Uma questão usa vários SVGs e um SVG pode ser usado por várias questões.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.database.models.asset import Asset
    from backend.database.models.questao import Question


class QuestionAsset(Base):
    __tablename__ = 'question_assets'

    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('questions.id', ondelete='CASCADE'), primary_key=True
    )
    asset_id: Mapped[str] = mapped_column(
        String(50), ForeignKey('assets.id', ondelete='RESTRICT'), primary_key=True, index=True
    )
    role: Mapped[str | None] = mapped_column(String(30))  # molécula principal, alternativa...

    question: Mapped[Question] = relationship(back_populates='asset_links')
    asset: Mapped[Asset] = relationship(back_populates='question_links')
