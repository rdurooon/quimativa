"""Configuração compartilhada dos testes."""
import pytest

from backend import config
from backend.database import conexao


@pytest.fixture(autouse=True)
def pasta_dados(tmp_path, monkeypatch):
    """Cada teste usa um banco próprio numa pasta temporária.

    Assim os testes nunca tocam no banco real do usuário.
    """
    monkeypatch.setenv(config.VAR_DATA_DIR, str(tmp_path))
    conexao.fechar_conexoes()
    yield tmp_path
    conexao.fechar_conexoes()
