"""Pacotes de questões disponíveis no banco local."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, novo_id

if TYPE_CHECKING:
    from backend.database.models.questao import Question


BASE_PACKAGE_ID = 'base'
BASE_PACKAGE_NAME = 'Questões-base'


class QuestionPackage(Base):
    __tablename__ = 'question_packages'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=novo_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_key: Mapped[str] = mapped_column(String(600), nullable=False, unique=True)

    questions: Mapped[list[Question]] = relationship(
        back_populates='package', passive_deletes=True
    )

    def __repr__(self) -> str:
        return f'<QuestionPackage {self.id} {self.name}>'
