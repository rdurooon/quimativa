"""Teste da migração de pacotes a partir do schema 0004."""
from alembic import command
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend import config
from backend.database import conexao
from backend.database.inicializacao import _config_alembic


def test_migracao_associa_somente_questoes_base_e_preserva_demais_origens(pasta_dados):
    assert pasta_dados.is_dir()
    url = config.obter_url_banco()
    cfg = _config_alembic(url)
    command.upgrade(cfg, '0004')

    engine = conexao.criar_engine(url)
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO questions
                (id, minigame_type, difficulty, source_type, statement, payload,
                 source_id, status, remote_id, remote_version, created_at, updated_at)
            VALUES
                ('base-q', 'identification', 1, 'base', 'Base', '{}',
                 NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                ('local-q', 'identification', 1, 'local', 'Local', '{}',
                 NULL, NULL, NULL, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                ('remote-q', 'identification', 1, 'remote', 'Remote', '{}',
                 NULL, NULL, 'remote-q', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """))
        conn.execute(text("""
            INSERT INTO assets (id, source_type, file_path, asset_type, name, checksum, created_at)
            VALUES
                ('base-asset', 'base', 'base.svg', 'svg', 'Base', NULL, CURRENT_TIMESTAMP),
                ('local-asset', 'local', 'local.svg', 'svg', 'Local', NULL, CURRENT_TIMESTAMP),
                ('remote-asset', 'remote', 'remote.svg', 'svg', 'Remote', NULL, CURRENT_TIMESTAMP)
        """))
        conn.execute(text("""
            INSERT INTO question_assets (question_id, asset_id, role)
            VALUES
                ('base-q', 'base-asset', 'molecule'),
                ('local-q', 'local-asset', 'molecule'),
                ('remote-q', 'remote-asset', 'molecule')
        """))
    engine.dispose()

    command.upgrade(cfg, 'head')
    engine = conexao.criar_engine(url)
    with engine.connect() as conn:
        packages = conn.execute(text('SELECT id, name FROM question_packages')).all()
        questions = conn.execute(
            text('SELECT id, source_type, package_id FROM questions ORDER BY id')
        ).all()
        assets = conn.execute(
            text('SELECT id, source_type, file_path, asset_type, name, checksum FROM assets ORDER BY id')
        ).all()
        links = conn.execute(
            text('SELECT question_id, asset_id, role FROM question_assets ORDER BY question_id, asset_id')
        ).all()
        assert conn.execute(text('PRAGMA foreign_key_check')).all() == []

    assert packages == [('base', 'Questões-base')]
    assert questions == [
        ('base-q', 'base', 'base'),
        ('local-q', 'local', None),
        ('remote-q', 'remote', None),
    ]
    assert assets == [
        ('base-asset', 'base', 'base.svg', 'svg', 'Base', None),
        ('local-asset', 'local', 'local.svg', 'svg', 'Local', None),
        ('remote-asset', 'remote', 'remote.svg', 'svg', 'Remote', None),
    ]
    assert links == [
        ('base-q', 'base-asset', 'molecule'),
        ('local-q', 'local-asset', 'molecule'),
        ('remote-q', 'remote-asset', 'molecule'),
    ]
    for sql in (
        "UPDATE questions SET package_id = 'base' WHERE id = 'local-q'",
        "UPDATE questions SET package_id = 'inexistente' WHERE id = 'local-q'",
        "UPDATE questions SET package_id = NULL WHERE id = 'base-q'",
    ):
        try:
            with engine.begin() as conn:
                conn.execute(text(sql))
        except IntegrityError:
            continue
        pytest.fail(f'A migração aceitou a associação inválida: {sql}')
    engine.dispose()

    command.downgrade(cfg, '0004')
    command.upgrade(cfg, 'head')
    engine = conexao.criar_engine(url)
    with engine.connect() as conn:
        assert conn.execute(text('SELECT count(*) FROM questions')).scalar_one() == 3
        assert conn.execute(text('SELECT count(*) FROM question_packages')).scalar_one() == 1
        assert conn.execute(text('PRAGMA foreign_key_check')).all() == []
        assert conn.execute(
            text('SELECT id, source_type, file_path, asset_type, name, checksum FROM assets ORDER BY id')
        ).all() == assets
        assert conn.execute(
            text('SELECT question_id, asset_id, role FROM question_assets ORDER BY question_id, asset_id')
        ).all() == links
    engine.dispose()
