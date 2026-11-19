"""Marco inicial do banco (sem tabelas).

As tabelas de questões entram na Entrega 2, após a definição do modelo.

Revision ID: 0001
Revises:
Create Date: 2026-11-19

"""
from typing import Sequence, Union

revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
