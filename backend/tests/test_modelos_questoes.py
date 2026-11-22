"""Testes das tabelas do banco de questões (estrutura e integridade)."""
import time

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from backend.database import conexao
from backend.database.inicializacao import inicializar_banco
from backend.database.models import Question, QuestionAsset, QuestionSource, Tag, question_tags
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
            assets=[QuestionAsset(file_path='base/moleculas/etanol.png', asset_type='imagem', role='molecula')],
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
        assert q.assets[0].file_path == 'base/moleculas/etanol.png'
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


def test_excluir_questao_remove_assets_e_vinculos_mas_mantem_tags():
    with conexao.sessao() as s:
        q = nova_questao(
            tags=[Tag(name='Álcool')],
            assets=[QuestionAsset(file_path='local/a.png', asset_type='imagem')],
        )
        s.add(q)
    with conexao.sessao() as s:
        s.delete(s.get(Question, q.id))
    with conexao.sessao() as s:
        assert contar(s, Question) == 0
        assert contar(s, QuestionAsset) == 0
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
