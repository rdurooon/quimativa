"""Classe base dos modelos SQLAlchemy."""
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Nomes fixos para índices e restrições. O Alembic precisa disso para
# alterar tabelas no SQLite (modo "batch") sem se perder.
CONVENCAO_NOMES = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


class Base(DeclarativeBase):
    """Todos os modelos herdam desta classe."""

    metadata = MetaData(naming_convention=CONVENCAO_NOMES)
