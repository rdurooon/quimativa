"""Testes do schema do minijogo Identificação de função orgânica."""
import copy

import pytest
from pydantic import ValidationError

from backend.questoes.schemas import (
    IdentificationPayload,
    validar_payload,
)

VALIDO = {
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


def payload(**mudancas):
    dados = copy.deepcopy(VALIDO)
    dados.update(mudancas)
    return dados


def test_payload_valido():
    p = IdentificationPayload.model_validate(VALIDO)
    assert p.correct_alternative_id == 'A'
    assert p.model_dump() == VALIDO  # ida e volta sem perda


def test_remove_espacos_das_pontas():
    p = IdentificationPayload.model_validate(payload(molecule_asset_id='  asset-001  '))
    assert p.molecule_asset_id == 'asset-001'


@pytest.mark.parametrize('qtd', [0, 3, 5])
def test_exige_exatamente_quatro_alternativas(qtd):
    alternativas = [{'id': str(i), 'label': f'Função {i}'} for i in range(qtd)]
    with pytest.raises(ValidationError):
        IdentificationPayload.model_validate(payload(alternatives=alternativas, correct_alternative_id='0'))


def test_rejeita_ids_de_alternativa_repetidos():
    dados = payload()
    dados['alternatives'][1]['id'] = 'A'
    with pytest.raises(ValidationError, match='IDs de alternativa repetidos'):
        IdentificationPayload.model_validate(dados)


@pytest.mark.parametrize('texto', ['Álcool', ' álcool ', 'ÁLCOOL'])
def test_rejeita_alternativas_com_mesmo_texto(texto):
    dados = payload()
    dados['alternatives'][1]['label'] = texto
    with pytest.raises(ValidationError, match='mesmo texto'):
        IdentificationPayload.model_validate(dados)


def test_rejeita_resposta_correta_inexistente():
    with pytest.raises(ValidationError, match='não está entre as alternativas'):
        IdentificationPayload.model_validate(payload(correct_alternative_id='E'))


@pytest.mark.parametrize('campo', ['molecule_asset_id', 'highlight', 'alternatives', 'correct_alternative_id'])
def test_campos_obrigatorios(campo):
    dados = payload()
    del dados[campo]
    with pytest.raises(ValidationError):
        IdentificationPayload.model_validate(dados)


@pytest.mark.parametrize('mudanca', [
    {'molecule_asset_id': '   '},
    {'highlight': {'region_id': ''}},
    {'highlight': {}},
])
def test_rejeita_referencias_vazias(mudanca):
    with pytest.raises(ValidationError):
        IdentificationPayload.model_validate(payload(**mudanca))


def test_rejeita_alternativa_com_texto_vazio():
    dados = payload()
    dados['alternatives'][2]['label'] = '  '
    with pytest.raises(ValidationError):
        IdentificationPayload.model_validate(dados)


def test_rejeita_campos_desconhecidos():
    with pytest.raises(ValidationError):
        IdentificationPayload.model_validate(payload(campo_extra='x'))


def test_validar_payload_escolhe_o_schema_pelo_minijogo():
    assert isinstance(validar_payload('identification', VALIDO), IdentificationPayload)


def test_minijogo_inexistente():
    with pytest.raises(ValueError):
        validar_payload('jogo_inexistente', {})


def test_assets_e_regioes_referenciados():
    p = IdentificationPayload.model_validate(VALIDO)
    assert p.assets_referenciados() == {'asset-001'}
    assert p.regioes_referenciadas() == {'asset-001': {'group-01'}}
