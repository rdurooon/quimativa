"""Testes da tabela app_metadata."""
import pytest

from backend.database import conexao
from backend.database.inicializacao import inicializar_banco
from backend.database.metadados import (
    definir_metadado,
    definir_versao_base,
    obter_metadado,
    obter_versao_base,
)


@pytest.fixture(autouse=True)
def banco(pasta_dados):
    inicializar_banco()


def test_metadado_inexistente_devolve_padrao():
    with conexao.sessao() as s:
        assert obter_metadado(s, 'nada') is None
        assert obter_metadado(s, 'nada', 'x') == 'x'


def test_define_e_sobrescreve_metadado():
    with conexao.sessao() as s:
        definir_metadado(s, 'chave', '1')
    with conexao.sessao() as s:
        definir_metadado(s, 'chave', '2')
    with conexao.sessao() as s:
        assert obter_metadado(s, 'chave') == '2'


def test_versao_do_conteudo_base():
    with conexao.sessao() as s:
        assert obter_versao_base(s) is None  # banco novo: nada instalado
        definir_versao_base(s, 3)
    with conexao.sessao() as s:
        assert obter_versao_base(s) == 3
