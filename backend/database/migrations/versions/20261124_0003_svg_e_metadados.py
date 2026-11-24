"""Assets somente SVG e tabela app_metadata.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'app_metadata',
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('key', name=op.f('pk_app_metadata')),
    )

    # SQLite não altera restrições diretamente: o modo batch recria a tabela.
    with op.batch_alter_table('question_assets') as tabela:
        tabela.create_check_constraint(
            op.f('ck_question_assets_asset_type_valido'), "asset_type IN ('svg')"
        )


def downgrade() -> None:
    with op.batch_alter_table('question_assets') as tabela:
        tabela.drop_constraint(op.f('ck_question_assets_asset_type_valido'), type_='check')
    op.drop_table('app_metadata')
