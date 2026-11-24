"""Testes do formato do pacote de questões-base."""
import copy
import uuid

import pytest
from pydantic import ValidationError

from backend.questoes.schemas.pacote_base import PacoteQuestoesBase

QUESTAO = {
    'id': '3f2b1c9e-8d4a-4f6b-9c1e-2a7d5e8f0b13',
    'minigame_type': 'identification',
    'difficulty': 1,
    'statement': 'Qual função orgânica está destacada?',
    'payload': {
        'molecule_asset_id': 'etanol',
        'highlight': {'region_id': 'grupo-oh'},
        'alternatives': [
            {'id': 'A', 'label': 'Álcool'},
            {'id': 'B', 'label': 'Cetona'},
            {'id': 'C', 'label': 'Éster'},
            {'id': 'D', 'label': 'Aldeído'},
        ],
        'correct_alternative_id': 'A',
    },
    'tags': ['Álcool', 'Grupo funcional'],
    'source': {'name': 'ENEM 2023', 'notes': 'Enunciado simplificado'},
}
ASSETS = [{'id': 'etanol', 'file': 'alcoois/etanol.svg', 'name': 'Etanol'}]


def pacote(*questoes, version=1, assets=None):
    return {
        'version': version,
        'assets': copy.deepcopy(ASSETS) if assets is None else assets,
        'questions': list(questoes) or [copy.deepcopy(QUESTAO)],
    }


def questao(**mudancas):
    q = copy.deepcopy(QUESTAO)
    q.update(mudancas)
    return q


def test_pacote_valido():
    p = PacoteQuestoesBase.model_validate(pacote(questao(), questao(id=str(uuid.uuid4()))))
    assert p.version == 1
    assert len(p.questions) == 2
    assert p.questions[0].payload == QUESTAO['payload']
    assert p.questions[0].source.name == 'ENEM 2023'
    assert p.assets[0].file == 'alcoois/etanol.svg'


def test_mesmo_asset_em_varias_questoes():
    PacoteQuestoesBase.model_validate(pacote(questao(), questao(id=str(uuid.uuid4()))))


def test_id_e_obrigatorio():
    q = questao()
    del q['id']
    with pytest.raises(ValidationError):
        PacoteQuestoesBase.model_validate(pacote(q))


def test_id_precisa_ser_uuid():
    with pytest.raises(ValidationError):
        PacoteQuestoesBase.model_validate(pacote(questao(id='questao-1')))


def test_ids_repetidos_no_pacote():
    with pytest.raises(ValidationError, match='IDs de questão repetidos'):
        PacoteQuestoesBase.model_validate(pacote(questao(), questao()))


def test_payload_invalido_e_rejeitado_com_detalhe():
    q = questao()
    q['payload']['correct_alternative_id'] = 'E'
    with pytest.raises(ValidationError, match='payload inválido'):
        PacoteQuestoesBase.model_validate(pacote(q))


def test_versao_minima():
    with pytest.raises(ValidationError):
        PacoteQuestoesBase.model_validate(pacote(version=0))


@pytest.mark.parametrize('campo, valor', [
    ('difficulty', 4),
    ('minigame_type', 'jogo_inexistente'),
    ('statement', '  '),
])
def test_campos_gerais_invalidos(campo, valor):
    with pytest.raises(ValidationError):
        PacoteQuestoesBase.model_validate(pacote(questao(**{campo: valor})))


def test_tags_repetidas():
    with pytest.raises(ValidationError, match='Tags repetidas'):
        PacoteQuestoesBase.model_validate(pacote(questao(tags=['Álcool', ' álcool'])))


def test_asset_usado_precisa_estar_declarado():
    with pytest.raises(ValidationError, match='não declarado'):
        PacoteQuestoesBase.model_validate(pacote(assets=[]))


@pytest.mark.parametrize('assets, mensagem', [
    ([{'id': 'etanol', 'file': 'a.svg'}, {'id': 'etanol', 'file': 'b.svg'}], 'IDs de asset repetidos'),
    ([{'id': 'etanol', 'file': 'a.svg'}, {'id': 'x', 'file': 'A.svg'}], 'Arquivos de asset repetidos'),
    ([{'id': 'etanol', 'file': '../fora.svg'}], 'Caminho de asset inválido'),
    ([{'id': 'etanol', 'file': 'etanol.png'}], '.svg'),
])
def test_assets_invalidos(assets, mensagem):
    with pytest.raises(ValidationError, match=mensagem):
        PacoteQuestoesBase.model_validate(pacote(assets=assets))
