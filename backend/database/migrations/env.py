"""Ambiente de execução das migrações do Alembic."""
from logging.config import fileConfig

from alembic import context

from backend import config
from backend.database import models  # noqa: F401  (registra os modelos no metadata)
from backend.database.base import Base
from backend.database.conexao import criar_engine

alembic_cfg = context.config

if alembic_cfg.config_file_name is not None:
    fileConfig(alembic_cfg.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _url_banco() -> str:
    """URL definida pelo chamador (ex.: testes) ou o banco padrão do usuário."""
    return alembic_cfg.get_main_option('sqlalchemy.url') or config.obter_url_banco()


def _executar(conexao) -> None:
    context.configure(
        connection=conexao,
        target_metadata=target_metadata,
        render_as_batch=True,  # necessário para ALTER TABLE no SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Gera o SQL sem conectar ao banco (alembic upgrade head --sql)."""
    context.configure(
        url=_url_banco(),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrações conectando ao banco."""
    # Uma conexão pronta pode ser passada pelo código (inicialização do app/testes).
    conexao = alembic_cfg.attributes.get('connection')
    if conexao is not None:
        _executar(conexao)
        return

    url = alembic_cfg.get_main_option('sqlalchemy.url') or None
    engine = criar_engine(url)
    try:
        with engine.connect() as conexao:
            _executar(conexao)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
