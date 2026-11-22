"""Tabelas do banco de questões.

questions, question_assets, tags, question_tags e question_sources.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Valores congelados nesta migração (não importar enums do código aqui).
MINIJOGOS = ("'identification', 'find_difference', 'card_association', "
             "'molecular_analysis', 'function_molecule', 'function_order'")
ORIGENS = "'base', 'local', 'remote'"


def upgrade() -> None:
    op.create_table(
        'question_sources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('reference', sa.Text(), nullable=True),
        sa.Column('license', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_question_sources')),
    )

    op.create_table(
        'tags',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
        sa.UniqueConstraint('name', name=op.f('uq_tags_name')),
    )

    op.create_table(
        'questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('minigame_type', sa.String(length=30), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=10), nullable=False),
        sa.Column('statement', sa.Text(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('source_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('remote_id', sa.String(length=100), nullable=True),
        sa.Column('remote_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint(f'minigame_type IN ({MINIJOGOS})', name=op.f('ck_questions_minigame_type_valido')),
        sa.CheckConstraint('difficulty BETWEEN 1 AND 3', name=op.f('ck_questions_difficulty_valida')),
        sa.CheckConstraint(f'source_type IN ({ORIGENS})', name=op.f('ck_questions_source_type_valido')),
        sa.CheckConstraint("(source_type = 'remote') = (remote_id IS NOT NULL)",
                           name=op.f('ck_questions_remote_id_somente_remotas')),
        sa.ForeignKeyConstraint(['source_id'], ['question_sources.id'],
                                name=op.f('fk_questions_source_id_question_sources'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_questions')),
    )
    op.create_index(op.f('ix_questions_minigame_type'), 'questions', ['minigame_type'], unique=False)
    op.create_index(op.f('ix_questions_difficulty'), 'questions', ['difficulty'], unique=False)
    op.create_index(op.f('ix_questions_source_type'), 'questions', ['source_type'], unique=False)
    op.create_index(op.f('ix_questions_remote_id'), 'questions', ['remote_id'], unique=True)

    op.create_table(
        'question_assets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('asset_type', sa.String(length=30), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=True),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'],
                                name=op.f('fk_question_assets_question_id_questions'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_question_assets')),
    )
    op.create_index(op.f('ix_question_assets_question_id'), 'question_assets', ['question_id'], unique=False)

    op.create_table(
        'question_tags',
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('tag_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'],
                                name=op.f('fk_question_tags_question_id_questions'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'],
                                name=op.f('fk_question_tags_tag_id_tags'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('question_id', 'tag_id', name=op.f('pk_question_tags')),
    )
    op.create_index(op.f('ix_question_tags_tag_id'), 'question_tags', ['tag_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_question_tags_tag_id'), table_name='question_tags')
    op.drop_table('question_tags')
    op.drop_index(op.f('ix_question_assets_question_id'), table_name='question_assets')
    op.drop_table('question_assets')
    op.drop_index(op.f('ix_questions_remote_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_source_type'), table_name='questions')
    op.drop_index(op.f('ix_questions_difficulty'), table_name='questions')
    op.drop_index(op.f('ix_questions_minigame_type'), table_name='questions')
    op.drop_table('questions')
    op.drop_table('tags')
    op.drop_table('question_sources')
