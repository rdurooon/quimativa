"""Assets reaproveitáveis: tabela `assets` + `question_assets` vira ligação N:N.

Antes: cada asset pertencia a uma única questão.
Agora: o mesmo SVG pode ser usado por várias questões. Registros antigos são
convertidos (cada asset antigo vira um asset novo ligado à sua questão).

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ORIGENS = "'base', 'local', 'remote'"


def upgrade() -> None:
    op.create_table(
        'assets',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('source_type', sa.String(length=10), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('asset_type', sa.String(length=30), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("asset_type IN ('svg')", name=op.f('ck_assets_asset_type_valido')),
        sa.CheckConstraint(f'source_type IN ({ORIGENS})', name=op.f('ck_assets_source_type_valido')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_assets')),
        sa.UniqueConstraint('source_type', 'file_path', name=op.f('uq_assets_source_type')),
    )
    op.create_index(op.f('ix_assets_source_type'), 'assets', ['source_type'], unique=False)

    # Converte os assets antigos (um por questão) para a tabela nova.
    op.execute(
        'INSERT INTO assets (id, source_type, file_path, asset_type, checksum, created_at) '
        'SELECT qa.id, q.source_type, qa.file_path, qa.asset_type, qa.checksum, CURRENT_TIMESTAMP '
        'FROM question_assets qa JOIN questions q ON q.id = qa.question_id'
    )

    op.drop_index(op.f('ix_question_assets_question_id'), table_name='question_assets')
    op.rename_table('question_assets', '_question_assets_antiga')

    op.create_table(
        'question_assets',
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('asset_id', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'],
                                name=op.f('fk_question_assets_question_id_questions'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'],
                                name=op.f('fk_question_assets_asset_id_assets'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('question_id', 'asset_id', name=op.f('pk_question_assets')),
    )
    op.create_index(op.f('ix_question_assets_asset_id'), 'question_assets', ['asset_id'], unique=False)

    op.execute(
        'INSERT INTO question_assets (question_id, asset_id, role) '
        'SELECT question_id, id, role FROM _question_assets_antiga'
    )
    op.drop_table('_question_assets_antiga')


def downgrade() -> None:
    op.drop_index(op.f('ix_question_assets_asset_id'), table_name='question_assets')
    op.rename_table('question_assets', '_question_assets_nova')

    op.create_table(
        'question_assets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('asset_type', sa.String(length=30), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=True),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.CheckConstraint("asset_type IN ('svg')", name=op.f('ck_question_assets_asset_type_valido')),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'],
                                name=op.f('fk_question_assets_question_id_questions'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_question_assets')),
    )
    op.create_index(op.f('ix_question_assets_question_id'), 'question_assets', ['question_id'], unique=False)

    op.execute(
        'INSERT INTO question_assets (id, question_id, file_path, asset_type, role, checksum) '
        'SELECT lower(hex(randomblob(16))), l.question_id, a.file_path, a.asset_type, l.role, a.checksum '
        'FROM _question_assets_nova l JOIN assets a ON a.id = l.asset_id'
    )
    op.drop_table('_question_assets_nova')
    op.drop_index(op.f('ix_assets_source_type'), table_name='assets')
    op.drop_table('assets')
