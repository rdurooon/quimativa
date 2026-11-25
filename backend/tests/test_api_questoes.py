"""Testes da bridge de questões (o que o frontend recebe)."""
import json

import pytest

from backend import config
from backend.api import API
from backend.database.inicializacao import inicializar_banco
from backend.questoes import servico
from backend.questoes.importador import importar_pacote_base

EXEMPLO = config.BASE_DIR / 'docs' / 'pacote_base_exemplo'
SVG = '<svg xmlns="http://www.w3.org/2000/svg"><g id="g1"/></svg>'


@pytest.fixture
def api(pasta_dados, monkeypatch):
    monkeypatch.setattr(config, 'ASSETS_BASE_DIR', EXEMPLO / 'assets')
    inicializar_banco()
    importar_pacote_base(EXEMPLO / 'pacote_base.json', EXEMPLO / 'assets')
    return API()


def dados():
    return {
        'minigame_type': 'function_molecule',
        'difficulty': 1,
        'statement': 'Qual molécula corresponde à função álcool?',
        'payload': {
            'cards': [
                {'id': 'C1', 'asset_id': 'etanol'},
                {'id': 'C2', 'asset_id': 'metilamina'},
                {'id': 'C3', 'asset_id': 'propanona'},
                {'id': 'C4', 'asset_id': 'etanal'},
            ],
            'correct_card_id': 'C1',
        },
    }


def test_fluxo_completo_pela_bridge(api):
    criada = api.questoes_criar(dados())
    assert criada['ok'] is True
    qid = criada['dados']['id']

    assert api.questoes_obter(qid)['dados']['statement'] == 'Qual molécula corresponde à função álcool?'
    assert api.questoes_listar({'source_type': 'local'})['dados']['total'] == 1

    novo = dados()
    novo['statement'] = 'Editada'
    assert api.questoes_atualizar(qid, novo)['dados']['statement'] == 'Editada'

    assert api.questoes_remover(qid) == {'ok': True, 'dados': {'id': qid}}
    assert api.questoes_obter(qid)['erro']['codigo'] == 'nao_encontrado'


def test_respostas_sao_serializaveis_em_json(api):
    qid = api.questoes_criar(dados())['dados']['id']
    for resposta in (
        api.questoes_metadados(), api.questoes_listar(), api.questoes_obter(qid),
        api.assets_listar(), api.assets_obter('etanol'), api.assets_importar_svg(SVG, 'Teste'),
    ):
        assert resposta['ok'] is True
        json.dumps(resposta)


def test_erro_de_validacao_vem_em_portugues(api):
    d = dados()
    d['payload']['cards'] = d['payload']['cards'][:3]
    r = api.questoes_criar(d)
    assert r['ok'] is False
    assert r['erro']['codigo'] == 'dados_invalidos'
    assert {'campo': 'payload.cards', 'mensagem': 'Precisa ter pelo menos 4 item(ns)'} in r['erro']['detalhes']


def test_erro_de_permissao(api):
    r = api.questoes_remover('5b0e7c52-3f7e-4d8a-9a51-1c2f4e6b8d01')
    assert r == {'ok': False, 'erro': {
        'codigo': 'nao_permitido', 'mensagem': 'Questões-base não podem ser removidas', 'detalhes': []}}


def test_erro_inesperado_nao_quebra_a_tela(api, monkeypatch):
    def explodir(*_):
        raise RuntimeError('falha simulada')

    monkeypatch.setattr(servico, 'obter_metadados', explodir)
    r = api.questoes_metadados()
    assert r['ok'] is False
    assert r['erro']['codigo'] == 'erro_interno'


def test_importar_svg_invalido(api):
    r = api.assets_importar_svg('<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>')
    assert r['erro']['codigo'] == 'dados_invalidos'
    assert 'script' in r['erro']['detalhes'][0]['mensagem']


def test_ping(api):
    assert api.ping() == 'pong'
