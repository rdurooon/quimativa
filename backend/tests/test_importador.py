"""Testes do importador do pacote de questões-base (usa docs/pacote_base_exemplo)."""
import json
import shutil

import pytest
from sqlalchemy import func, select

from backend import config
from backend.database import conexao
from backend.database.inicializacao import inicializar_banco
from backend.database.metadados import obter_versao_base
from backend.database.models import Asset, Question, QuestionAsset, QuestionSource
from backend.questoes.erros import ErroPacoteBase
from backend.questoes.importador import importar_pacote_base

EXEMPLO = config.BASE_DIR / 'docs' / 'pacote_base_exemplo'


@pytest.fixture
def pacote(tmp_path, pasta_dados):
    """Cópia do pacote de exemplo numa pasta temporária (pode ser alterada no teste)."""
    inicializar_banco()
    destino = tmp_path / 'pacote'
    shutil.copytree(EXEMPLO, destino)
    return destino


def importar(pasta, **kw):
    return importar_pacote_base(pasta / 'pacote_base.json', pasta / 'assets', **kw)


def ler(pasta):
    return json.loads((pasta / 'pacote_base.json').read_text(encoding='utf-8'))


def gravar(pasta, dados):
    (pasta / 'pacote_base.json').write_text(json.dumps(dados, ensure_ascii=False), encoding='utf-8')


def contar(alvo, *condicoes):
    with conexao.sessao() as s:
        return s.scalar(select(func.count()).select_from(alvo).where(*condicoes))


def test_importa_pacote_de_exemplo(pacote):
    r = importar(pacote)
    assert r.status == 'importado'
    assert (r.questoes_inseridas, r.assets_inseridos) == (6, 6)
    assert contar(Question, Question.source_type == 'base') == 6
    assert contar(Asset, Asset.source_type == 'base') == 6
    with conexao.sessao() as s:
        assert obter_versao_base(s) == 1
        q = s.get(Question, '5b0e7c52-3f7e-4d8a-9a51-1c2f4e6b8d06')
        assert {l.asset_id for l in q.asset_links} == {
            'etanol', 'metilamina', 'etanamida', 'etanoato-de-metila'}
        assert q.source.name == 'Documento mestre do Quimativa'
        assert len(s.get(Asset, 'etanol').checksum) == 64


def test_svg_reaproveitado_entre_questoes(pacote):
    importar(pacote)
    assert contar(QuestionAsset, QuestionAsset.asset_id == 'etanol') == 4


def test_importar_de_novo_nao_duplica(pacote):
    importar(pacote)
    r = importar(pacote)
    assert r.status == 'ja_atualizado'
    assert contar(Question) == 6
    assert contar(Asset) == 6


def test_forcar_reimportacao_sem_mudancas(pacote):
    importar(pacote)
    r = importar(pacote, forcar=True)
    assert (r.questoes_inseridas, r.questoes_atualizadas, r.assets_inseridos, r.assets_atualizados) == (0, 0, 0, 0)
    assert contar(Question) == 6


def test_nova_versao_atualiza_somente_o_que_mudou(pacote):
    importar(pacote)
    dados = ler(pacote)
    dados['version'] = 2
    dados['questions'][0]['statement'] = 'Enunciado revisado'
    dados['questions'][0]['tags'] = ['Álcool']
    gravar(pacote, dados)

    r = importar(pacote)
    assert r.status == 'importado'
    assert (r.questoes_inseridas, r.questoes_atualizadas) == (0, 1)
    with conexao.sessao() as s:
        q = s.get(Question, dados['questions'][0]['id'])
        assert q.statement == 'Enunciado revisado'
        assert [t.name for t in q.tags] == ['Álcool']
        assert obter_versao_base(s) == 2


def test_nova_versao_troca_svg_de_uma_questao(pacote):
    importar(pacote)
    dados = ler(pacote)
    dados['version'] = 2
    dados['questions'][1]['payload']['molecules'][0]['asset_id'] = 'etanal'
    gravar(pacote, dados)
    importar(pacote)
    with conexao.sessao() as s:
        q = s.get(Question, dados['questions'][1]['id'])
        assert {l.asset_id for l in q.asset_links} == {'etanal', 'etanoato-de-metila'}


def test_remover_fonte_na_nova_versao(pacote):
    importar(pacote)
    dados = ler(pacote)
    dados['version'] = 2
    del dados['questions'][5]['source']
    gravar(pacote, dados)
    importar(pacote)
    assert contar(QuestionSource) == 0


def test_pacote_mais_antigo_e_ignorado(pacote):
    dados = ler(pacote)
    dados['version'] = 5
    gravar(pacote, dados)
    importar(pacote)
    dados['version'] = 4
    dados['questions'][0]['statement'] = 'não deve entrar'
    gravar(pacote, dados)
    assert importar(pacote).status == 'pacote_mais_antigo'
    with conexao.sessao() as s:
        assert s.get(Question, dados['questions'][0]['id']).statement != 'não deve entrar'


def test_sem_pacote(tmp_path, pasta_dados):
    inicializar_banco()
    assert importar(tmp_path).status == 'sem_pacote'


def test_questao_retirada_do_pacote_e_mantida_e_listada(pacote):
    importar(pacote)
    dados = ler(pacote)
    removida = dados['questions'].pop(0)
    dados['version'] = 2
    gravar(pacote, dados)
    r = importar(pacote)
    assert r.questoes_fora_do_pacote == [removida['id']]
    assert contar(Question) == 6


# --- Erros: nada pode ser gravado ---------------------------------------------

def nada_gravado():
    with conexao.sessao() as s:
        assert obter_versao_base(s) is None
    assert contar(Question) == 0
    assert contar(Asset) == 0


def test_svg_inexistente(pacote):
    (pacote / 'assets' / 'alcoois' / 'etanol.svg').unlink()
    with pytest.raises(ErroPacoteBase, match='arquivo não encontrado'):
        importar(pacote)
    nada_gravado()


def test_svg_malicioso(pacote):
    (pacote / 'assets' / 'alcoois' / 'etanol.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><g id="grupo-oh"/><script>alert(1)</script></svg>')
    with pytest.raises(ErroPacoteBase, match='<script>'):
        importar(pacote)
    nada_gravado()


def test_regiao_destacada_inexistente_no_svg(pacote):
    dados = ler(pacote)
    dados['questions'][0]['payload']['highlight']['region_id'] = 'grupo-xyz'
    gravar(pacote, dados)
    with pytest.raises(ErroPacoteBase, match='grupo-xyz'):
        importar(pacote)
    nada_gravado()


def test_json_invalido(pacote):
    (pacote / 'pacote_base.json').write_text('{ "version": 1, ', encoding='utf-8')
    with pytest.raises(ErroPacoteBase, match='JSON inválido'):
        importar(pacote)


def test_payload_invalido_aponta_o_campo(pacote):
    dados = ler(pacote)
    dados['questions'][0]['payload']['alternatives'].pop()
    gravar(pacote, dados)
    with pytest.raises(ErroPacoteBase) as erro:
        importar(pacote)
    assert 'payload.alternatives' in str(erro.value)
    assert 'pelo menos 4' in str(erro.value)
    nada_gravado()


def test_conflito_com_questao_local_de_mesmo_id(pacote):
    dados = ler(pacote)
    with conexao.sessao() as s:
        s.add(Question(id=dados['questions'][0]['id'], minigame_type='identification', difficulty=1,
                       source_type='local', statement='x', payload={}))
    with pytest.raises(ErroPacoteBase, match='já existe com origem "local"'):
        importar(pacote)
    assert contar(Question) == 1
