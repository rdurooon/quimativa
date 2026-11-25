"""Pacotes locais e associação opcional às questões.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BASE_PACKAGE_ID = 'base'
BASE_PACKAGE_NAME = 'Questões-base'
BASE_PACKAGE_NAME_KEY = 'questões-base'


def upgrade() -> None:
    op.create_table(
        'question_packages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('name_key', sa.String(length=600), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_question_packages')),
        sa.UniqueConstraint('name_key', name=op.f('uq_question_packages_name_key')),
    )
    op.bulk_insert(
        sa.table(
            'question_packages',
            sa.column('id', sa.String()),
            sa.column('name', sa.String()),
            sa.column('name_key', sa.String()),
        ),
        [{'id': BASE_PACKAGE_ID, 'name': BASE_PACKAGE_NAME, 'name_key': BASE_PACKAGE_NAME_KEY}],
    )

    op.execute(
        'ALTER TABLE questions ADD COLUMN package_id VARCHAR(36) '
        'REFERENCES question_packages (id) ON DELETE SET NULL'
    )

    op.execute(
        sa.text("UPDATE questions SET package_id = :package_id WHERE source_type = 'base'")
        .bindparams(package_id=BASE_PACKAGE_ID)
    )

    regra_origem_pacote = (
        "(NEW.source_type = 'base' AND NEW.package_id IS 'base') OR "
        "(NEW.source_type != 'base' AND "
        "(NEW.package_id IS NULL OR NEW.package_id IS NOT 'base'))"
    )
    op.execute(f"""
        CREATE TRIGGER questions_package_origin_insert
        BEFORE INSERT ON questions
        WHEN NOT ({regra_origem_pacote})
        BEGIN
            SELECT RAISE(ABORT, 'origem e pacote de questão inconsistentes');
        END
    """)
    op.execute(f"""
        CREATE TRIGGER questions_package_origin_update
        BEFORE UPDATE OF source_type, package_id ON questions
        WHEN NOT ({regra_origem_pacote})
        BEGIN
            SELECT RAISE(ABORT, 'origem e pacote de questão inconsistentes');
        END
    """)
    op.create_index(op.f('ix_questions_package_id'), 'questions', ['package_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_questions_package_id'), table_name='questions')
    op.execute('DROP TRIGGER questions_package_origin_update')
    op.execute('DROP TRIGGER questions_package_origin_insert')
    op.execute('ALTER TABLE questions DROP COLUMN package_id')
    op.drop_table('question_packages')
