"""Conexão com o banco SQLite: engine, sessões e ciclo de vida.

Uso típico nas camadas de repositório/serviço:

    from backend.database.conexao import sessao

    with sessao() as s:
        s.add(objeto)
    # commit automático ao sair do bloco; rollback se ocorrer erro
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from backend import config

_engine: Engine | None = None
_fabrica_sessoes: sessionmaker[Session] | None = None


def texto_para_busca(texto: str | None) -> str:
    """Forma usada na busca: sem acentos, sem diferença de maiúsculas e com espaços simples."""
    if texto is None:
        return ""
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c)
    )
    return " ".join(sem_acentos.split()).casefold()


def _configurar_sqlite(conexao_dbapi, _registro) -> None:
    """Executado a cada nova conexão com o SQLite."""
    # O LIKE do SQLite só ignora maiúsculas em letras sem acento; a busca usa esta função.
    conexao_dbapi.create_function(
        "quimativa_busca", 1, texto_para_busca, deterministic=True
    )
    cursor = conexao_dbapi.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")  # SQLite vem com FKs desligadas
    cursor.execute("PRAGMA journal_mode=WAL")  # leituras e escritas mais seguras
    cursor.execute(
        "PRAGMA busy_timeout=5000"
    )  # espera até 5s se o banco estiver ocupado
    cursor.close()


def criar_engine(url: str | None = None, *, echo: bool = False) -> Engine:
    """Cria uma engine nova. Sem URL, usa o banco padrão do usuário."""
    if url is None:
        config.garantir_diretorios()
        url = config.obter_url_banco()
    # check_same_thread=False: o PyWebView chama a API em threads diferentes.
    engine = create_engine(url, echo=echo, connect_args={"check_same_thread": False})
    event.listen(engine, "connect", _configurar_sqlite)
    return engine


def obter_engine() -> Engine:
    """Engine única do aplicativo (criada na primeira chamada)."""
    global _engine
    if _engine is None:
        _engine = criar_engine()
    return _engine


def obter_fabrica_sessoes() -> sessionmaker[Session]:
    global _fabrica_sessoes
    if _fabrica_sessoes is None:
        # expire_on_commit=False: os dados continuam acessíveis após o commit,
        # o que facilita converter o resultado para enviar ao frontend.
        _fabrica_sessoes = sessionmaker(bind=obter_engine(), expire_on_commit=False)
    return _fabrica_sessoes


@contextmanager
def sessao() -> Iterator[Session]:
    """Abre uma sessão com commit automático e rollback em caso de erro."""
    s = obter_fabrica_sessoes()()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def fechar_conexoes() -> None:
    """Fecha a engine e esquece a configuração atual.

    Usado ao encerrar o app e nos testes (para trocar de banco).
    """
    global _engine, _fabrica_sessoes
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _fabrica_sessoes = None
