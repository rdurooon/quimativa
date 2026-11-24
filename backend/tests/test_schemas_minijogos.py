"""Testes dos schemas dos minijogos 2 a 6 (o 1 está em test_schemas_identificacao.py)."""
import copy

import pytest
from pydantic import ValidationError

from backend.questoes.schemas import SCHEMAS_PAYLOAD, validar_payload
from backend.questoes.tipos import MinigameType as T


def mol(i: int) -> dict:
    return {'id': f'M{i}', 'asset_id': f'asset-{i:03d}'}


VALIDOS = {
    T.FIND_DIFFERENCE: {
        'molecules': [mol(1), mol(2), mol(3)],
        'criterion': 'Possui função éster',
        'correct_molecule_id': 'M2',
    },
    T.CARD_ASSOCIATION: {
        'cards': [
            {'id': 'C1', 'asset_id': 'asset-001'},
            {'id': 'C2', 'content': 'Álcool'},
            {'id': 'C3', 'asset_id': 'asset-002'},
            {'id': 'C4', 'content': 'Cetona'},
        ],
        'correct_pair': ['C1', 'C2'],
    },
    T.MOLECULAR_ANALYSIS: {
        'molecule_asset_id': 'asset-005',
        'question': 'Qual é a classificação da cadeia carbônica?',
        'alternatives': [
            {'id': 'A', 'label': 'Aberta'},
            {'id': 'B', 'label': 'Fechada'},
            {'id': 'C', 'label': 'Mista'},
            {'id': 'D', 'label': 'Aromática'},
        ],
        'correct_alternative_id': 'A',
    },
    T.FUNCTION_MOLECULE: {
        'target_function': 'Éster',
        'molecules': [mol(6), mol(7), mol(8)],
        'correct_molecule_id': 'M7',
    },
    T.FUNCTION_ORDER: {
        'requested_order': ['Álcool', 'Éster', 'Amida', 'Amina'],
        'molecules': [mol(1), mol(2), mol(3), mol(4)],
        'correct_order': ['M1', 'M4', 'M3', 'M2'],
    },
}


def validar(tipo, alterar=None):
    dados = copy.deepcopy(VALIDOS[tipo])
    if alterar:
        alterar(dados)
    return validar_payload(tipo, dados)


# --- Geral ------------------------------------------------------------------

def test_todos_os_minijogos_tem_schema():
    assert set(SCHEMAS_PAYLOAD) == set(T)


@pytest.mark.parametrize('tipo', list(VALIDOS))
def test_payload_valido_ida_e_volta(tipo):
    assert validar(tipo).model_dump(exclude_none=True) == VALIDOS[tipo]


@pytest.mark.parametrize('tipo', list(VALIDOS))
def test_rejeita_campo_desconhecido(tipo):
    with pytest.raises(ValidationError):
        validar(tipo, lambda d: d.update(campo_extra='x'))


# --- Casos inválidos (tipo, alteração, trecho esperado da mensagem) ---------

INVALIDOS = [
    # Encontre a diferença
    (T.FIND_DIFFERENCE, lambda d: d.update(molecules=[mol(1)], correct_molecule_id='M1'), None),
    (T.FIND_DIFFERENCE, lambda d: d['molecules'][1].update(id='M1'), 'IDs de molécula repetidos'),
    (T.FIND_DIFFERENCE, lambda d: d['molecules'][1].update(asset_id='asset-001'), 'mais de uma vez'),
    (T.FIND_DIFFERENCE, lambda d: d.update(correct_molecule_id='M9'), 'não está entre as moléculas'),
    (T.FIND_DIFFERENCE, lambda d: d.update(criterion='   '), None),
    # Associação de cartas
    (T.CARD_ASSOCIATION, lambda d: d['cards'].pop(), None),
    (T.CARD_ASSOCIATION, lambda d: d['cards'].append({'id': 'C5', 'content': 'Éter'}), None),
    (T.CARD_ASSOCIATION, lambda d: d['cards'].__setitem__(1, {'id': 'C2'}), 'precisa de texto'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][1].update(id='C1'), 'IDs de carta repetidos'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][3].update(content=' álcool'), 'mesmo conteúdo'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][2].update(asset_id='asset-001'), 'mais de uma vez'),
    (T.CARD_ASSOCIATION, lambda d: d.update(correct_pair=['C1', 'C1']), 'duas cartas diferentes'),
    (T.CARD_ASSOCIATION, lambda d: d.update(correct_pair=['C1', 'C9']), 'não existe'),
    (T.CARD_ASSOCIATION, lambda d: d.update(correct_pair=['C1', 'C2', 'C3']), None),
    # Análise molecular
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(alternatives=d['alternatives'][:1]), None),
    (T.MOLECULAR_ANALYSIS, lambda d: d['alternatives'][1].update(label='ABERTA'), 'mesmo texto'),
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(correct_alternative_id='E'), 'não está entre as alternativas'),
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(question=''), None),
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(highlight={'region_id': ''}), None),
    # Qual molécula pertence à função?
    (T.FUNCTION_MOLECULE, lambda d: d.update(target_function=' '), None),
    (T.FUNCTION_MOLECULE, lambda d: d.update(molecules=[mol(7)]), None),
    (T.FUNCTION_MOLECULE, lambda d: d.update(correct_molecule_id='M1'), 'não está entre as moléculas'),
    # Ordem das funções
    (T.FUNCTION_ORDER, lambda d: d['requested_order'].pop(), None),
    (T.FUNCTION_ORDER, lambda d: d['requested_order'].__setitem__(3, 'álcool '), 'Funções repetidas'),
    (T.FUNCTION_ORDER, lambda d: d['molecules'].pop(), None),
    (T.FUNCTION_ORDER, lambda d: d['molecules'][1].update(asset_id='asset-001'), 'mais de uma vez'),
    (T.FUNCTION_ORDER, lambda d: d.update(correct_order=['M1', 'M1', 'M3', 'M2']), 'exatamente uma vez'),
    (T.FUNCTION_ORDER, lambda d: d.update(correct_order=['M1', 'M4', 'M3', 'M9']), 'exatamente uma vez'),
]


@pytest.mark.parametrize('tipo, alterar, mensagem', INVALIDOS)
def test_payload_invalido(tipo, alterar, mensagem):
    with pytest.raises(ValidationError, match=mensagem):
        validar(tipo, alterar)


# --- Casos válidos específicos ------------------------------------------------

def test_encontre_diferenca_aceita_mais_de_tres_moleculas():
    validar(T.FIND_DIFFERENCE, lambda d: d.update(molecules=[mol(i) for i in range(1, 6)]))


def test_carta_pode_ter_texto_e_imagem():
    validar(T.CARD_ASSOCIATION, lambda d: d['cards'][0].update(content='Estrutura A'))


def test_analise_molecular_aceita_destaque_opcional():
    p = validar(T.MOLECULAR_ANALYSIS, lambda d: d.update(highlight={'region_id': 'g1'}))
    assert p.highlight.region_id == 'g1'


# --- Assets e regiões referenciados -------------------------------------------

@pytest.mark.parametrize('tipo, esperado', [
    (T.FIND_DIFFERENCE, {'asset-001', 'asset-002', 'asset-003'}),
    (T.CARD_ASSOCIATION, {'asset-001', 'asset-002'}),
    (T.MOLECULAR_ANALYSIS, {'asset-005'}),
    (T.FUNCTION_MOLECULE, {'asset-006', 'asset-007', 'asset-008'}),
    (T.FUNCTION_ORDER, {'asset-001', 'asset-002', 'asset-003', 'asset-004'}),
])
def test_assets_referenciados(tipo, esperado):
    assert validar(tipo).assets_referenciados() == esperado


def test_regioes_referenciadas_da_analise_molecular():
    assert validar(T.MOLECULAR_ANALYSIS).regioes_referenciadas() == {}
    p = validar(T.MOLECULAR_ANALYSIS, lambda d: d.update(highlight={'region_id': 'g1'}))
    assert p.regioes_referenciadas() == {'asset-005': {'g1'}}
