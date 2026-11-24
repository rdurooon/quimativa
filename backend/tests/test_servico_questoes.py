"""Testes do serviço de questões e de assets (regras de negócio)."""
import copy
import json
import shutil

import pytest
from sqlalchemy import func, select

from backend import config
from backend.database import conexao
from backend.database.inicializacao import inicializar_banco
from backend.database.models import Asset, Question, QuestionSource, Tag
from backend.questoes import assets as servico_assets
from backend.questoes import servico
from backend.questoes.erros import DadosInvalidos, NaoEncontrado, OperacaoNaoPermitida
from backend.questoes.importador import importar_pacote_base

EXEMPLO = config.BASE_DIR / 'docs' / 'pacote_base_exemplo'
ID_BASE = '5b0e7c52-3f7e-4d8a-9a51-1c2f4e6b8d01'  # questão-base do exemplo (identificação)

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
       '<g id="grupo-cooh"><circle cx="5" cy="5" r="2"/></g></svg>')


@pytest.fixture(autouse=True)
def ambiente(pasta_dados, monkeypatch):
    """Banco novo + questões-base do pacote de exemplo."""
    monkeypatch.setattr(config, 'ASSETS_BASE_DIR', EXEMPLO / 'assets')
    inicializar_banco()
    importar_pacote_base(EXEMPLO / 'pacote_base.json', EXEMPLO / 'assets')


@pytest.fixture
def svg_local():
    return servico_assets.importar_svg_local(SVG, 'Ácido etanoico')


def dados_questao(asset_id='etanol', regiao='grupo-oh', **mudancas):
    dados = {
        'minigame_type': 'identification',
        'difficulty': 2,
        'statement': 'Qual função está destacada?',
        'payload': {
            'molecule_asset_id': asset_id,
            'highlight': {'region_id': regiao},
            'alternatives': [
                {'id': 'A', 'label': 'Álcool'}, {'id': 'B', 'label': 'Ácido carboxílico'},
                {'id': 'C', 'label': 'Éster'}, {'id': 'D', 'label': 'Aldeído'},
            ],
            'correct_alternative_id': 'A',
        },
        'tags': ['Álcool'],
    }
    dados.update(mudancas)
    return dados


def contar(alvo, *condicoes):
    with conexao.sessao() as s:
        return s.scalar(select(func.count()).select_from(alvo).where(*condicoes))


# --- Criar / obter --------------------------------------------------------------

def test_criar_questao_local_usando_svg_da_base():
    q = servico.criar_questao_local(dados_questao())
    assert q['source_type'] == 'local'
    assert q['permissions'] == {'edit': True, 'delete': True}
    assert q['minigame_name'] == 'Identificação de função orgânica'
    assert q['difficulty_name'] == 'Média'
    assert q['assets']['etanol']['data_uri'].startswith('data:image/svg+xml;base64,')
    assert servico.obter_questao(q['id']) == q


def test_criar_questao_local_com_svg_local(svg_local):
    q = servico.criar_questao_local(
        dados_questao(svg_local['id'], 'grupo-cooh', source={'name': 'ENEM 2022', 'notes': 'Adaptada'}))
    assert set(q['assets']) == {svg_local['id']}
    assert q['source'] == {'name': 'ENEM 2022', 'reference': None, 'license': None, 'notes': 'Adaptada'}


def test_resultado_e_serializavel_em_json():
    q = servico.criar_questao_local(dados_questao())
    json.dumps(q)
    json.dumps(servico.listar_questoes())
    json.dumps(servico.obter_metadados())
    json.dumps(servico_assets.listar_assets())


def test_tags_reaproveitadas_sem_diferenciar_maiusculas():
    servico.criar_questao_local(dados_questao(tags=[' álcool ', 'Novo   assunto']))
    with conexao.sessao() as s:
        nomes = sorted(s.scalars(select(Tag.name)))
    assert 'álcool' not in nomes and 'Álcool' in nomes
    assert 'Novo assunto' in nomes


def test_obter_inexistente():
    with pytest.raises(NaoEncontrado):
        servico.obter_questao('nao-existe')


# --- Validação ----------------------------------------------------------------------

def detalhes(erro):
    return {(d['campo'], d['mensagem']) for d in erro.value.detalhes}


def test_payload_invalido_aponta_o_campo_em_portugues():
    dados = dados_questao()
    dados['payload']['alternatives'].pop()
    with pytest.raises(DadosInvalidos) as erro:
        servico.criar_questao_local(dados)
    assert ('payload.alternatives', 'Precisa ter pelo menos 4 item(ns)') in detalhes(erro)


def test_campos_gerais_invalidos():
    with pytest.raises(DadosInvalidos) as erro:
        servico.criar_questao_local(dados_questao(statement='  ', difficulty=7, extra=1))
    campos = {d['campo'] for d in erro.value.detalhes}
    assert {'statement', 'difficulty', 'extra'} <= campos


def test_imagem_inexistente():
    with pytest.raises(DadosInvalidos) as erro:
        servico.criar_questao_local(dados_questao(asset_id='nao-existe'))
    assert ('payload', 'Imagem "nao-existe" não encontrada') in detalhes(erro)


def test_regiao_inexistente_no_svg():
    with pytest.raises(DadosInvalidos) as erro:
        servico.criar_questao_local(dados_questao(regiao='grupo-xyz'))
    assert any('grupo-xyz' in m for _, m in detalhes(erro))


@pytest.mark.parametrize('dados', [None, [], 'texto'])
def test_formato_invalido(dados):
    with pytest.raises(DadosInvalidos):
        servico.criar_questao_local(dados)


def test_nada_e_gravado_quando_ha_erro():
    antes = contar(Question)
    with pytest.raises(DadosInvalidos):
        servico.criar_questao_local(dados_questao(regiao='grupo-xyz', tags=['Tag nova']))
    assert contar(Question) == antes
    assert contar(Tag, Tag.name == 'Tag nova') == 0


# --- Editar ----------------------------------------------------------------------------

def test_editar_questao_local(svg_local):
    q = servico.criar_questao_local(dados_questao(source={'name': 'ENEM 2022'}))
    novo = dados_questao(svg_local['id'], 'grupo-cooh', statement='Novo enunciado', tags=['Ácido'])
    novo['payload']['correct_alternative_id'] = 'B'
    r = servico.atualizar_questao_local(q['id'], novo)
    assert r['statement'] == 'Novo enunciado'
    assert r['payload']['correct_alternative_id'] == 'B'
    assert set(r['assets']) == {svg_local['id']}
    assert r['tags'] == ['Ácido']
    assert r['source'] is None
    assert contar(QuestionSource) == 1  # só a fonte da questão-base do exemplo


def test_editar_fonte_mantem_o_mesmo_registro():
    q = servico.criar_questao_local(dados_questao(source={'name': 'ENEM 2022'}))
    servico.atualizar_questao_local(q['id'], dados_questao(source={'name': 'ENEM 2023'}))
    assert contar(QuestionSource) == 2
    assert servico.obter_questao(q['id'])['source']['name'] == 'ENEM 2023'


def test_editar_questao_base_e_proibido():
    with pytest.raises(OperacaoNaoPermitida, match='Questões-base não podem ser editadas'):
        servico.atualizar_questao_local(ID_BASE, dados_questao())


def test_editar_questao_remota_e_proibido():
    with conexao.sessao() as s:
        s.add(Question(id='r1', minigame_type='identification', difficulty=1, source_type='remote',
                       remote_id='site-1', statement='x', payload={}))
    with pytest.raises(OperacaoNaoPermitida, match='site'):
        servico.atualizar_questao_local('r1', dados_questao())


def test_editar_com_dados_invalidos_nao_altera_nada():
    q = servico.criar_questao_local(dados_questao())
    with pytest.raises(DadosInvalidos):
        servico.atualizar_questao_local(q['id'], dados_questao(statement=''))
    assert servico.obter_questao(q['id'])['statement'] == q['statement']


# --- Remover ----------------------------------------------------------------------------

def test_remover_questao_local_apaga_svg_local_sem_uso(svg_local):
    q = servico.criar_questao_local(dados_questao(svg_local['id'], 'grupo-cooh'))
    arquivo = config.obter_assets_dir('local') / f'{svg_local["id"]}.svg'
    assert arquivo.exists()
    servico.remover_questao(q['id'])
    assert contar(Question, Question.id == q['id']) == 0
    assert contar(Asset, Asset.id == svg_local['id']) == 0
    assert not arquivo.exists()


def test_remover_mantem_svg_local_usado_por_outra_questao(svg_local):
    q1 = servico.criar_questao_local(dados_questao(svg_local['id'], 'grupo-cooh'))
    servico.criar_questao_local(dados_questao(svg_local['id'], 'grupo-cooh'))
    servico.remover_questao(q1['id'])
    assert contar(Asset, Asset.id == svg_local['id']) == 1


def test_remover_questao_local_nunca_apaga_svg_da_base():
    q = servico.criar_questao_local(dados_questao())
    servico.remover_questao(q['id'])
    assert contar(Asset, Asset.id == 'etanol') == 1
    assert (EXEMPLO / 'assets' / 'alcoois' / 'etanol.svg').exists()


def test_remover_questao_base_e_proibido():
    with pytest.raises(OperacaoNaoPermitida):
        servico.remover_questao(ID_BASE)


def test_remover_copia_de_questao_remota():
    with conexao.sessao() as s:
        s.add(Question(id='r1', minigame_type='identification', difficulty=1, source_type='remote',
                       remote_id='site-1', statement='x', payload={}))
    servico.remover_questao('r1')
    assert contar(Question, Question.id == 'r1') == 0


# --- Listar ---------------------------------------------------------------------------------

def test_listar_com_filtros():
    servico.criar_questao_local(dados_questao(statement='Questão local sobre etanol', tags=['Etanol']))
    assert servico.listar_questoes()['total'] == 7
    assert servico.listar_questoes({'source_type': 'local'})['total'] == 1
    assert servico.listar_questoes({'source_type': 'base'})['total'] == 6
    assert servico.listar_questoes({'minigame_type': 'identification'})['total'] == 2
    assert servico.listar_questoes({'difficulty': 3})['total'] == 1
    assert servico.listar_questoes({'tag': 'ÉSTER'})['total'] == 2
    assert servico.listar_questoes({'tag': 'não existe'})['total'] == 0
    assert servico.listar_questoes({'busca': 'sobre etanol'})['total'] == 1


def test_listar_paginado_e_sem_gabarito():
    r = servico.listar_questoes({'limite': 2, 'deslocamento': 1})
    assert len(r['items']) == 2 and r['total'] == 6
    assert 'payload' not in r['items'][0]


def test_listar_com_filtro_invalido():
    with pytest.raises(DadosInvalidos) as erro:
        servico.listar_questoes({'difficulty': 9, 'limite': 0})
    assert {'filtros.difficulty', 'filtros.limite'} <= {d['campo'] for d in erro.value.detalhes}


def test_metadados():
    m = servico.obter_metadados()
    assert len(m['minigames']) == 6
    assert m['difficulties'][0] == {'value': 1, 'name': 'Fácil'}
    base = next(o for o in m['source_types'] if o['value'] == 'base')
    assert base == {'value': 'base', 'name': 'Base', 'can_create': False, 'edit': False, 'delete': False}


# --- Assets -----------------------------------------------------------------------------------

def test_importar_svg_local(svg_local):
    assert svg_local['source_type'] == 'local'
    assert svg_local['name'] == 'Ácido etanoico'
    assert svg_local['permissions'] == {'delete': True}
    assert (config.obter_assets_dir('local') / f'{svg_local["id"]}.svg').read_text() == SVG


def test_importar_mesmo_svg_duas_vezes_reaproveita(svg_local):
    de_novo = servico_assets.importar_svg_local(SVG, 'outro nome')
    assert de_novo['id'] == svg_local['id']
    assert contar(Asset, Asset.source_type == 'local') == 1


def test_importar_svg_malicioso():
    with pytest.raises(DadosInvalidos, match='SVG inválido'):
        servico_assets.importar_svg_local('<svg xmlns="http://www.w3.org/2000/svg" onload="x()"/>')
    assert not config.obter_assets_dir('local').exists() or not any(config.obter_assets_dir('local').iterdir())


def test_listar_assets():
    assert len(servico_assets.listar_assets('base')) == 6
    assert servico_assets.listar_assets('local') == []
    etanol = next(a for a in servico_assets.listar_assets() if a['id'] == 'etanol')
    assert etanol['usage_count'] == 4
    assert etanol['permissions'] == {'delete': False}


def test_obter_asset_com_conteudo():
    a = servico_assets.obter_asset('etanol')
    assert a['data_uri'].startswith('data:image/svg+xml;base64,')
    with pytest.raises(NaoEncontrado):
        servico_assets.obter_asset('nao-existe')


def test_remover_asset_local_sem_uso(svg_local):
    servico_assets.remover_asset(svg_local['id'])
    assert contar(Asset, Asset.id == svg_local['id']) == 0
    assert not (config.obter_assets_dir('local') / f'{svg_local["id"]}.svg').exists()


def test_remover_asset_em_uso_e_proibido(svg_local):
    servico.criar_questao_local(dados_questao(svg_local['id'], 'grupo-cooh'))
    with pytest.raises(OperacaoNaoPermitida, match='em uso'):
        servico_assets.remover_asset(svg_local['id'])


def test_remover_asset_base_e_proibido():
    with pytest.raises(OperacaoNaoPermitida):
        servico_assets.remover_asset('etanol')
