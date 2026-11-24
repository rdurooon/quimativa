"""Inicialização segura do banco: aplica as migrações pendentes ao abrir o app.

- Banco novo: cria todas as tabelas pela sequência de migrações.
- Banco existente e desatualizado: faz uma cópia de segurança e atualiza.
- Banco já atualizado: não faz nada (pode rodar quantas vezes quiser).
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

from backend import config
from backend.database.conexao import criar_engine

log = logging.getLogger(__name__)

BACKUPS_MANTIDOS = 3

PASTA_MIGRACOES = config.BACKEND_DIR / 'database' / 'migrations'


def _config_alembic(url: str) -> Config:
    """Configuração do Alembic montada em código (não depende do alembic.ini,
    que não vai junto no executável)."""
    cfg = Config()
    cfg.set_main_option('script_location', str(PASTA_MIGRACOES))
    cfg.set_main_option('sqlalchemy.url', url)
    return cfg


def _revisao_atual(engine: Engine) -> str | None:
    with engine.connect() as conexao:
        return MigrationContext.configure(conexao).get_current_revision()


def _fazer_backup(caminho_banco: Path, revisao: str | None) -> Path:
    """Copia o banco usando a API de backup do SQLite (segura com WAL)."""
    destino = caminho_banco.with_name(f'{caminho_banco.stem}.backup-{revisao or "vazio"}.db')
    origem = sqlite3.connect(caminho_banco)
    copia = sqlite3.connect(destino)
    try:
        origem.backup(copia)
    finally:
        copia.close()
        origem.close()
    return destino


def _limpar_backups_antigos(caminho_banco: Path, manter: int = BACKUPS_MANTIDOS) -> None:
    """Mantém só os backups mais recentes do banco."""
    backups = sorted(
        caminho_banco.parent.glob(f'{caminho_banco.stem}.backup-*.db'),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for antigo in backups[manter:]:
        try:
            antigo.unlink()
        except OSError:
            log.warning('Não foi possível apagar o backup antigo %s', antigo)


def inicializar_banco(url: str | None = None) -> str:
    """Garante que o banco existe e está na versão mais recente.

    Sem URL, usa o banco padrão do usuário. Devolve a revisão final.
    """
    usando_padrao = url is None
    if usando_padrao:
        config.garantir_diretorios()
        url = config.obter_url_banco()

    cfg = _config_alembic(url)
    revisao_final = ScriptDirectory.from_config(cfg).get_current_head()

    engine = criar_engine(url)
    try:
        revisao = _revisao_atual(engine)
        if revisao == revisao_final:
            return revisao

        caminho = config.obter_caminho_banco()
        if usando_padrao and revisao is not None and caminho.exists():
            backup = _fazer_backup(caminho, revisao)
            log.info('Backup do banco criado em %s', backup)
            _limpar_backups_antigos(caminho)

        with engine.begin() as conexao:
            cfg.attributes['connection'] = conexao
            command.upgrade(cfg, 'head')

        log.info('Banco atualizado de %s para %s', revisao, revisao_final)
        return revisao_final
    finally:
        engine.dispose()
