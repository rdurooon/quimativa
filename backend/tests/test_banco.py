"""Testes da fundação do banco: configuração, conexão, migrações e persistência."""
import sqlite3
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend import config
from backend.database import conexao
from backend.database import models  # noqa: F401  (registra os modelos)
from backend.database.base import Base
from backend.database.inicializacao import _config_alembic, _fazer_backup, inicializar_banco


def _revisao_mais_recente() -> str:
    cfg = _config_alembic(config.obter_url_banco())
    return ScriptDirectory.from_config(cfg).get_current_head()


def _criar_tabela_teste() -> None:
    with conexao.sessao() as s:
        s.execute(text('CREATE TABLE teste (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)'))


# --- Configuração -----------------------------------------------------------

def test_banco_usa_pasta_de_dados_configurada(pasta_dados):
    assert config.obter_caminho_banco() == pasta_dados / config.NOME_BANCO


def test_pasta_padrao_fica_fora_da_pasta_temporaria(monkeypatch):
    """O banco não pode ficar onde o PyInstaller extrai os arquivos (pasta temp)."""
    monkeypatch.delenv(config.VAR_DATA_DIR, raising=False)
    pasta = config.obter_data_dir().resolve()
    assert pasta.name == config.NOME_APP
    assert Path(tempfile.gettempdir()).resolve() not in pasta.parents


# --- Inicialização e migrações ----------------------------------------------

def test_inicializacao_cria_banco_na_versao_atual():
    revisao = inicializar_banco()
    assert config.obter_caminho_banco().exists()
    assert revisao == _revisao_mais_recente()


def test_inicializacao_e_idempotente(pasta_dados):
    assert inicializar_banco() == inicializar_banco()
    assert not list(pasta_dados.glob('*.backup-*'))


def test_migracoes_sobem_e_descem():
    config.garantir_diretorios()
    url = config.obter_url_banco()
    cfg = _config_alembic(url)

    command.upgrade(cfg, 'head')
    command.downgrade(cfg, 'base')
    command.upgrade(cfg, 'head')

    engine = conexao.criar_engine(url)
    try:
        with engine.connect() as c:
            assert MigrationContext.configure(c).get_current_revision() == _revisao_mais_recente()
    finally:
        engine.dispose()


def test_modelos_e_migracoes_estao_sincronizados():
    """Falha se alguém criar/alterar um modelo e esquecer de gerar a migração."""
    inicializar_banco()
    engine = conexao.criar_engine(config.obter_url_banco())
    try:
        with engine.connect() as c:
            # SQLite não preserva/reflete o nome de uma FK adicionada por ALTER TABLE.
            def incluir_objeto(objeto, _nome, tipo, _refletido, _comparado):
                if tipo == 'foreign_key_constraint':
                    if 'package_id' in {coluna.name for coluna in objeto.columns}:
                        return False
                return True

            diferencas = compare_metadata(
                MigrationContext.configure(c, opts={'include_object': incluir_objeto}),
                Base.metadata,
            )
            fks = c.execute(text("PRAGMA foreign_key_list('questions')")).all()
            fk_pacote = next(fk for fk in fks if fk[3] == 'package_id')
            assert (fk_pacote[2], fk_pacote[4], fk_pacote[6]) == (
                'question_packages', 'id', 'SET NULL'
            )
    finally:
        engine.dispose()
    assert diferencas == [], f'Modelos sem migração: {diferencas}'


def test_backup_copia_o_conteudo_do_banco():
    inicializar_banco()
    _criar_tabela_teste()
    with conexao.sessao() as s:
        s.execute(text("INSERT INTO teste (nome) VALUES ('etanol')"))
    conexao.fechar_conexoes()

    backup = _fazer_backup(config.obter_caminho_banco(), '0001')
    c = sqlite3.connect(backup)
    try:
        assert c.execute('SELECT nome FROM teste').fetchone() == ('etanol',)
    finally:
        c.close()


# --- Conexão, persistência e integridade ------------------------------------

def test_pragmas_da_conexao():
    with conexao.sessao() as s:
        assert s.execute(text('PRAGMA foreign_keys')).scalar() == 1
        assert s.execute(text('PRAGMA journal_mode')).scalar() == 'wal'


def test_dados_persistem_apos_fechar_o_app():
    inicializar_banco()
    _criar_tabela_teste()
    with conexao.sessao() as s:
        s.execute(text("INSERT INTO teste (nome) VALUES ('etanol')"))

    conexao.fechar_conexoes()  # simula fechar e abrir o aplicativo

    with conexao.sessao() as s:
        assert s.execute(text('SELECT nome FROM teste')).scalar_one() == 'etanol'


def test_criar_ler_atualizar_e_excluir():
    _criar_tabela_teste()
    with conexao.sessao() as s:
        s.execute(text("INSERT INTO teste (id, nome) VALUES (1, 'metano')"))
    with conexao.sessao() as s:
        s.execute(text("UPDATE teste SET nome = 'etano' WHERE id = 1"))
    with conexao.sessao() as s:
        assert s.execute(text('SELECT nome FROM teste WHERE id = 1')).scalar_one() == 'etano'
        s.execute(text('DELETE FROM teste WHERE id = 1'))
    with conexao.sessao() as s:
        assert s.execute(text('SELECT COUNT(*) FROM teste')).scalar_one() == 0


def test_sessao_desfaz_alteracoes_quando_ha_erro():
    _criar_tabela_teste()
    with pytest.raises(RuntimeError):
        with conexao.sessao() as s:
            s.execute(text("INSERT INTO teste (nome) VALUES ('propano')"))
            raise RuntimeError('falha simulada')
    with conexao.sessao() as s:
        assert s.execute(text('SELECT COUNT(*) FROM teste')).scalar_one() == 0


def test_chaves_estrangeiras_sao_respeitadas():
    with conexao.sessao() as s:
        s.execute(text('CREATE TABLE pai (id INTEGER PRIMARY KEY)'))
        s.execute(text('CREATE TABLE filho (id INTEGER PRIMARY KEY, '
                       'pai_id INTEGER NOT NULL REFERENCES pai(id))'))
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.execute(text('INSERT INTO filho (pai_id) VALUES (999)'))


def test_migracao_0004_converte_assets_antigos():
    """Assets no formato antigo (um por questão) viram assets reaproveitáveis."""
    config.garantir_diretorios()
    url = config.obter_url_banco()
    cfg = _config_alembic(url)
    command.upgrade(cfg, '0003')

    engine = conexao.criar_engine(url)
    try:
        with engine.begin() as c:
            c.execute(text(
                "INSERT INTO questions (id, minigame_type, difficulty, source_type, statement, payload, "
                "created_at, updated_at) VALUES ('q1', 'identification', 1, 'local', 'x', '{}', "
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ))
            c.execute(text(
                "INSERT INTO question_assets (id, question_id, file_path, asset_type, role) "
                "VALUES ('a1', 'q1', 'etanol.svg', 'svg', 'molecula')"
            ))
    finally:
        engine.dispose()

    command.upgrade(cfg, 'head')

    engine = conexao.criar_engine(url)
    try:
        with engine.connect() as c:
            assert c.execute(text('SELECT id, source_type, file_path FROM assets')).all() == [
                ('a1', 'local', 'etanol.svg')
            ]
            assert c.execute(text('SELECT question_id, asset_id, role FROM question_assets')).all() == [
                ('q1', 'a1', 'molecula')
            ]
    finally:
        engine.dispose()


def test_mantem_somente_os_ultimos_backups(pasta_dados):
    import os

    from backend.database.inicializacao import BACKUPS_MANTIDOS, _limpar_backups_antigos

    banco = pasta_dados / config.NOME_BANCO
    for i in range(5):
        arquivo = pasta_dados / f'{banco.stem}.backup-000{i}.db'
        arquivo.write_bytes(b'x')
        os.utime(arquivo, (1000 + i, 1000 + i))

    _limpar_backups_antigos(banco)

    restantes = sorted(p.name for p in pasta_dados.glob('*.backup-*.db'))
    assert len(restantes) == BACKUPS_MANTIDOS
    assert restantes == [f'{banco.stem}.backup-000{i}.db' for i in (2, 3, 4)]
