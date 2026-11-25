"""Migração segura de payloads antigos de Qual molécula."""
import copy

import pytest
from alembic import command
from sqlalchemy import select

from backend import config
from backend.database import conexao
from backend.database.inicializacao import _config_alembic
from backend.database.models import AppMetadata, Asset, Question, QuestionAsset
from backend.questoes.migracoes_payloads import (
    CHAVE_MIGRACAO_QUAL_MOLECULA,
    migrar_payloads_qual_molecula,
)


def molecula(indice: int, asset_id: str | None = None) -> dict:
    return {'id': f'M{indice}', 'asset_id': asset_id or f'asset-{indice:03d}'}


def payload_legado(qtd: int = 4) -> dict:
    return {
        'target_function': 'Amina',
        'molecules': [molecula(i) for i in range(1, qtd + 1)],
        'correct_molecule_id': 'M2',
    }


def nova_questao(questao_id: str, payload: object, minigame_type: str = 'function_molecule') -> Question:
    return Question(
        id=questao_id,
        minigame_type=minigame_type,
        difficulty=1,
        source_type='local',
        statement='Questão de teste',
        payload=payload,
    )


def obter_questao(s, questao_id: str) -> Question:
    questao = s.get(Question, questao_id)
    assert questao is not None
    return questao


@pytest.fixture
def banco_sem_migracao(pasta_dados):
    """Cria o schema atual sem executar a migração de dados do startup."""
    assert pasta_dados.is_dir()
    url = config.obter_url_banco()
    command.upgrade(_config_alembic(url), 'head')
    return url


def test_migra_payloads_conversiveis_sem_perda_e_reporta_os_demais(banco_sem_migracao):
    assert banco_sem_migracao.startswith('sqlite:///')
    payload_bom = payload_legado()
    payload_bom['molecules'][0]['supplementary_text'] = 'Detalhe preservado'
    assets = [
        Asset(id=f'asset-{i:03d}', source_type='local', file_path=f'{i}.svg')
        for i in range(1, 5)
    ]
    convertivel = nova_questao('legado-convertivel', payload_bom)
    convertivel.asset_links = [QuestionAsset(asset=asset) for asset in assets]
    curto = nova_questao('legado-curto', payload_legado(3))
    com_extra = payload_legado()
    com_extra['molecules'][0]['campo_legado'] = 'não descartar'
    extra = nova_questao('legado-com-extra', com_extra)
    asset_ausente = nova_questao(
        'legado-asset-ausente',
        payload_legado().copy() | {
            'molecules': [molecula(i, f'ausente-{i}') for i in range(1, 5)]
        },
    )
    atual = nova_questao('ja-atual', {
        'cards': [
            {'id': f'C{i}', 'content': f'Opção {i}'}
            for i in range(1, 5)
        ],
        'correct_card_id': 'C3',
    })
    nao_objeto = nova_questao('legado-nao-objeto', ['payload', 'inválido'])
    outro_jogo = nova_questao('outro-minijogo', {'molecules': ['intacto']}, 'identification')

    with conexao.sessao() as s:
        s.add_all([*assets, convertivel, curto, extra, asset_ausente, atual, nao_objeto, outro_jogo])
    with conexao.sessao() as s:
        vinculos_antes = s.execute(
            select(QuestionAsset.question_id, QuestionAsset.asset_id, QuestionAsset.role)
        ).all()
        payload_outro_antes = copy.deepcopy(obter_questao(s, 'outro-minijogo').payload)

    with conexao.sessao() as s:
        resultado = migrar_payloads_qual_molecula(s)

    assert resultado.convertidas == 1
    assert resultado.validas == 1
    assert {item['question_id'] for item in resultado.nao_convertidas} == {
        'legado-curto',
        'legado-com-extra',
        'legado-asset-ausente',
        'legado-nao-objeto',
    }
    motivos = {item['question_id']: item['reason'] for item in resultado.nao_convertidas}
    assert '4 item(ns)' in motivos['legado-curto']
    assert 'campo_legado' in motivos['legado-com-extra']
    assert 'ausente-1' in motivos['legado-asset-ausente']
    assert 'objeto JSON' in motivos['legado-nao-objeto']

    with conexao.sessao() as s:
        convertido = obter_questao(s, 'legado-convertivel')
        assert convertido.payload['target_function'] == 'Amina'
        assert [card['id'] for card in convertido.payload['cards']] == ['M1', 'M2', 'M3', 'M4']
        assert convertido.payload['cards'][0] == {
            'id': 'M1',
            'asset_id': 'asset-001',
            'supplementary_text': 'Detalhe preservado',
        }
        assert obter_questao(s, 'legado-curto').payload == payload_legado(3)
        assert obter_questao(s, 'legado-com-extra').payload == com_extra
        assert obter_questao(s, 'legado-asset-ausente').payload['molecules'][0]['asset_id'] == 'ausente-1'
        assert obter_questao(s, 'legado-nao-objeto').payload == ['payload', 'inválido']
        assert obter_questao(s, 'ja-atual').payload['correct_card_id'] == 'C3'
        assert obter_questao(s, 'outro-minijogo').payload == payload_outro_antes
        assert s.execute(
            select(QuestionAsset.question_id, QuestionAsset.asset_id, QuestionAsset.role)
        ).all() == vinculos_antes
        marcador = s.get(AppMetadata, CHAVE_MIGRACAO_QUAL_MOLECULA)
        assert marcador is not None

    with conexao.sessao() as s:
        repetido = migrar_payloads_qual_molecula(s)
    assert repetido.ja_aplicada is True
    assert repetido.convertidas == resultado.convertidas
    assert repetido.nao_convertidas == resultado.nao_convertidas


def test_rollback_preserva_payload_e_relacoes_se_a_transacao_falhar(banco_sem_migracao):
    assert banco_sem_migracao.startswith('sqlite:///')
    dados = payload_legado()
    assets = [
        Asset(id=f'asset-{i:03d}', source_type='local', file_path=f'{i}.svg')
        for i in range(1, 5)
    ]
    questao = nova_questao('legado-rollback', dados)
    questao.asset_links = [QuestionAsset(asset=asset) for asset in assets]
    with conexao.sessao() as s:
        s.add_all([*assets, questao])

    with pytest.raises(RuntimeError, match='falha simulada'):
        with conexao.sessao() as s:
            assert migrar_payloads_qual_molecula(s).convertidas == 1
            raise RuntimeError('falha simulada')

    with conexao.sessao() as s:
        questao = obter_questao(s, 'legado-rollback')
        assert questao.payload == dados
        assert {link.asset_id for link in questao.asset_links} == {
            f'asset-{i:03d}' for i in range(1, 5)
        }
        assert s.get(AppMetadata, CHAVE_MIGRACAO_QUAL_MOLECULA) is None
