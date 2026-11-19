"""Modelos do banco.

Todo modelo novo deve ser importado aqui para que o Alembic o enxergue
ao gerar migrações (alembic revision --autogenerate).
"""
from backend.database.base import Base

__all__ = ['Base']
