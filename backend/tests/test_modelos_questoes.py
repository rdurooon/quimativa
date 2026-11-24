"""Testes das tabelas do banco de questões (estrutura e integridade)."""
import time

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from backend.database import conexao
from backend.database.inicializacao import inicializar_banco
from backend.database.models import Asset, Question, QuestionAsset, QuestionSource, Tag, question_tags
from backend.questoes.tipos import Difficulty, MinigameType, SourceType

PAYLOAD = {
    'molecule_asset_id': 'asset-001',
    'highlight': {'region_id': 'group-01'},
    'alternatives': [
        {'id': 'A', 'label': 'Álcool'},
        {'id': 'B', 'label': 'Cetona'},
        {'id': 'C', 'label': 'Éster'},
        {'id': 'D', 'label': 'Aldeído'},
    ],
    'correct_alternative_id': 'A',
}


@pytest.fixture(autouse=True)
def banco(pasta_dados):
    inicializar_banco()


def nova_questao(**extra) -> Question:
    dados = dict(
        minigame_type=MinigameType.IDENTIFICATION,
        difficulty=Difficulty.EASY,
        source_type=SourceType.LOCAL,
        statement='Qual função orgânica está destacada?',
        payload=PAYLOAD,
    )
    dados.update(extra)
    return Question(**dados)


def contar(s, alvo) -> int:
    return s.scalar(select(func.count()).select_from(alvo))


def test_cria_e_le_questao_completa():
    with conexao.sessao() as s:
        q = nova_questao(
            source=QuestionSource(name='ENEM 2023', notes='Enunciado adaptado'),
            tags=[Tag(name='Álcool')],
            asset_links=[QuestionAsset(
                asset=Asset(id='asset-001', source_type='local', file_path='etanol.svg'), role='molecula'
            )],
        )
        s.add(q)
        s.flush()
        qid = q.id

    conexao.fechar_conexoes()

    with conexao.sessao() as s:
        q = s.get(Question, qid)
        assert len(q.id) == 36
        assert q.payload == PAYLOAD  # inclusive acentos
        assert q.minigame_type == 'identification'
        assert q.difficulty == 1
        assert q.source.name == 'ENEM 2023'
        assert [t.name for t in q.tags] == ['Álcool']
        assert q.asset_links[0].asset.file_path == 'etanol.svg'
        assert q.asset_links[0].asset.asset_type == 'svg'
        assert q.asset_links[0].role == 'molecula'
        assert q.created_at is not None and q.updated_at is not None


def test_updated_at_muda_ao_editar():
    with conexao.sessao() as s:
        q = nova_questao()
        s.add(q)
    antes = q.updated_at
    time.sleep(0.01)
    with conexao.sessao() as s:
        q = s.get(Question, q.id)
        q.statement = 'Novo enunciado'
    assert q.updated_at > antes


@pytest.mark.parametrize('campo, valor', [
    ('difficulty', 4),
    ('difficulty', 0),
    ('source_type', 'outra'),
    ('minigame_type', 'jogo_inexistente'),
])
def test_valores_invalidos_sao_rejeitados(campo, valor):
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.add(nova_questao(**{campo: valor}))


@pytest.mark.parametrize('origem, remote_id', [
    (SourceType.REMOTE, None),       # remota sem identificador remoto
    (SourceType.LOCAL, 'site-123'),  # local com identificador remoto
    (SourceType.BASE, 'site-123'),   # base com identificador remoto
])
def test_remote_id_somente_em_questoes_remotas(origem, remote_id):
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.add(nova_questao(source_type=origem, remote_id=remote_id))


def test_questao_remota_valida_e_remote_id_unico():
    with conexao.sessao() as s:
        s.add(nova_questao(source_type=SourceType.REMOTE, remote_id='site-1', remote_version='3'))
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.add(nova_questao(source_type=SourceType.REMOTE, remote_id='site-1'))


def test_excluir_questao_remove_vinculos_mas_mantem_tags_e_assets():
    with conexao.sessao() as s:
        q = nova_questao(
            tags=[Tag(name='Álcool')],
            asset_links=[QuestionAsset(asset=Asset(source_type='local', file_path='a.svg'))],
        )
        s.add(q)
    with conexao.sessao() as s:
        s.delete(s.get(Question, q.id))
    with conexao.sessao() as s:
        assert contar(s, Question) == 0
        assert contar(s, QuestionAsset) == 0
        assert contar(s, Asset) == 1  # o arquivo pode servir a outras questões
        assert contar(s, question_tags) == 0
        assert contar(s, Tag) == 1


def test_fonte_em_uso_nao_pode_ser_excluida():
    with conexao.sessao() as s:
        fonte = QuestionSource(name='ENEM 2023')
        s.add(nova_questao(source=fonte))
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.delete(s.get(QuestionSource, fonte.id))


def test_nome_de_tag_e_unico():
    with conexao.sessao() as s:
        s.add(Tag(name='Éster'))
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.add(Tag(name='Éster'))


def test_asset_aceita_somente_svg():
    with conexao.sessao() as s:
        s.add(Asset(source_type='local', file_path='a.svg'))
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.add(Asset(source_type='local', file_path='a.png', asset_type='png'))


def test_mesmo_asset_em_varias_questoes():
    with conexao.sessao() as s:
        etanol = Asset(id='etanol', source_type='base', file_path='etanol.svg')
        s.add_all([
            nova_questao(asset_links=[QuestionAsset(asset=etanol)]),
            nova_questao(asset_links=[QuestionAsset(asset=etanol)]),
        ])
    with conexao.sessao() as s:
        assert contar(s, Asset) == 1
        assert contar(s, QuestionAsset) == 2
        assert len(s.get(Asset, 'etanol').question_links) == 2


def test_asset_em_uso_nao_pode_ser_excluido():
    with conexao.sessao() as s:
        s.add(nova_questao(asset_links=[QuestionAsset(asset=Asset(id='x', source_type='local', file_path='x.svg'))]))
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.delete(s.get(Asset, 'x'))


def test_mesmo_arquivo_nao_e_registrado_duas_vezes_na_mesma_origem():
    with conexao.sessao() as s:
        s.add(Asset(source_type='local', file_path='a.svg'))
        s.add(Asset(source_type='base', file_path='a.svg'))  # outra origem: pode
    with pytest.raises(IntegrityError):
        with conexao.sessao() as s:
            s.add(Asset(source_type='local', file_path='a.svg'))
