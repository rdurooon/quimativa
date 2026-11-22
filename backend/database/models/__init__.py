"""Modelos do banco.

Todo modelo novo deve ser importado aqui para que o Alembic o enxergue
ao gerar migrações (alembic revision --autogenerate).
"""
from backend.database.base import Base
from backend.database.models.fonte_questao import QuestionSource
from backend.database.models.questao import Question, question_tags
from backend.database.models.questao_asset import QuestionAsset
from backend.database.models.tag import Tag

__all__ = ['Base', 'Question', 'QuestionAsset', 'QuestionSource', 'Tag', 'question_tags']
