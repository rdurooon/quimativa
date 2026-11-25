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
        'molecules': [mol(1), mol(2)],
        'correct_molecule_id': 'M2',
    },
    T.CARD_ASSOCIATION: {
        'cards': [
            {'id': 'C1', 'asset_id': 'asset-001', 'supplementary_text': 'Molécula A'},
            {'id': 'C2', 'content': 'Álcool'},
            {'id': 'C3', 'asset_id': 'asset-002'},
            {'id': 'C4', 'content': 'Cetona', 'supplementary_text': 'Grupo funcional'},
        ],
        'correct_pair': ['C1', 'C2'],
    },
    T.MOLECULAR_ANALYSIS: {
        'molecule_asset_id': 'asset-005',
        'highlight': {'region_id': 'grupo-oh'},
        'alternatives': [
            {'id': 'A', 'label': 'Aberta'},
            {'id': 'B', 'label': 'Fechada'},
            {'id': 'C', 'label': 'Mista'},
            {'id': 'D', 'label': 'Aromática'},
        ],
        'correct_alternative_id': 'A',
    },
    T.FUNCTION_MOLECULE: {
        'cards': [
            {'id': 'C1', 'asset_id': 'asset-006'},
            {'id': 'C2', 'content': 'Molécula B'},
            {'id': 'C3', 'asset_id': 'asset-008', 'supplementary_text': 'Opção 3'},
            {'id': 'C4', 'content': 'Molécula D'},
        ],
        'correct_card_id': 'C2',
    },
    T.FUNCTION_ORDER: {
        'molecules': [mol(1), mol(2), mol(3), mol(4)],
        'correct_order': ['M1', 'M4', 'M3', 'M2'],
    },
}


def validar(tipo, alterar=None):
    dados = copy.deepcopy(VALIDOS[tipo])
    if alterar:
        alterar(dados)
    return validar_payload(tipo, dados)


def test_todos_os_minijogos_tem_schema():
    assert set(SCHEMAS_PAYLOAD) == set(T)


@pytest.mark.parametrize('tipo', list(VALIDOS))
def test_payload_valido_ida_e_volta(tipo):
    assert validar(tipo).model_dump(exclude_none=True) == VALIDOS[tipo]


@pytest.mark.parametrize('tipo', list(VALIDOS))
def test_rejeita_campo_desconhecido(tipo):
    with pytest.raises(ValidationError):
        validar(tipo, lambda d: d.update(campo_extra='x'))


INVALIDOS = [
    # Encontre a diferença
    (T.FIND_DIFFERENCE, lambda d: d.update(molecules=[mol(1)]), None),
    (T.FIND_DIFFERENCE, lambda d: d['molecules'].append(mol(3)), None),
    (T.FIND_DIFFERENCE, lambda d: d['molecules'][1].update(id='M1'), 'IDs de molécula repetidos'),
    (T.FIND_DIFFERENCE, lambda d: d['molecules'][1].update(asset_id='asset-001'), 'mais de uma vez'),
    (T.FIND_DIFFERENCE, lambda d: d.update(correct_molecule_id='M9'), 'não está entre as moléculas'),
    (T.FIND_DIFFERENCE, lambda d: d.update(criterion='   '), None),
    # Associação de cartas
    (T.CARD_ASSOCIATION, lambda d: d['cards'].pop(), None),
    (T.CARD_ASSOCIATION, lambda d: d['cards'].append({'id': 'C5', 'content': 'Éter'}), None),
    (T.CARD_ASSOCIATION, lambda d: d['cards'].__setitem__(1, {'id': 'C2'}), 'exatamente um'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][1].update(id='C1'), 'IDs de carta repetidos'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][3].update(content=' álcool'), 'mesmo conteúdo'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][2].update(asset_id='asset-001'), 'mais de uma vez'),
    (T.CARD_ASSOCIATION, lambda d: d['cards'][0].update(content='Estrutura A'), 'exatamente um'),
    (T.CARD_ASSOCIATION, lambda d: d.update(correct_pair=['C1', 'C1']), 'duas cartas diferentes'),
    (T.CARD_ASSOCIATION, lambda d: d.update(correct_pair=['C1', 'C9']), 'não existe'),
    (T.CARD_ASSOCIATION, lambda d: d.update(correct_pair=['C1', 'C2', 'C3']), None),
    # Análise molecular
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(alternatives=d['alternatives'][:3]), None),
    (T.MOLECULAR_ANALYSIS, lambda d: d['alternatives'][1].update(label='ABERTA'), 'mesmo texto'),
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(correct_alternative_id='E'), 'não está entre as alternativas'),
    (T.MOLECULAR_ANALYSIS, lambda d: d.pop('highlight'), None),
    (T.MOLECULAR_ANALYSIS, lambda d: d.update(highlight={'region_id': ''}), None),
    # Qual molécula pertence à função?
    (T.FUNCTION_MOLECULE, lambda d: d['cards'].pop(), None),
    (T.FUNCTION_MOLECULE, lambda d: d['cards'][1].update(asset_id='asset-007'), 'exatamente um'),
    (T.FUNCTION_MOLECULE, lambda d: d.update(correct_card_id='C9'), 'carta correta'),
    (T.FUNCTION_MOLECULE, lambda d: d['cards'][3].update(content='molécula b'), 'mesmo conteúdo'),
    # Ordem das funções
    (T.FUNCTION_ORDER, lambda d: d['molecules'].pop(), None),
    (T.FUNCTION_ORDER, lambda d: d['molecules'][1].update(asset_id='asset-001'), 'mais de uma vez'),
    (T.FUNCTION_ORDER, lambda d: d.update(correct_order=['M1', 'M1', 'M3', 'M2']), 'exatamente uma vez'),
    (T.FUNCTION_ORDER, lambda d: d.update(correct_order=['M1', 'M4', 'M3', 'M9']), 'exatamente uma vez'),
    (T.FUNCTION_ORDER, lambda d: d['correct_order'].pop(), None),
]


@pytest.mark.parametrize('tipo, alterar, mensagem', INVALIDOS)
def test_payload_invalido(tipo, alterar, mensagem):
    with pytest.raises(ValidationError, match=mensagem):
        validar(tipo, alterar)


def test_criterio_legado_opcional_e_preservado():
    payload = validar(
        T.FIND_DIFFERENCE,
        lambda d: d.update(criterion='Possui função éster'),
    )
    assert payload.criterion == 'Possui função éster'


def test_payload_legado_de_qual_molecula_e_normalizado():
    molecules = [mol(i) for i in range(1, 5)]
    molecules[0]['supplementary_text'] = 'Detalhe preservado'
    payload = validar_payload(T.FUNCTION_MOLECULE, {
        'target_function': 'Amina',
        'molecules': molecules,
        'correct_molecule_id': 'M2',
    })
    assert [card.id for card in payload.cards] == ['M1', 'M2', 'M3', 'M4']
    assert payload.correct_card_id == 'M2'
    assert payload.target_function == 'Amina'
    assert payload.cards[0].supplementary_text == 'Detalhe preservado'


@pytest.mark.parametrize('tipo, esperado', [
    (T.FIND_DIFFERENCE, {'asset-001', 'asset-002'}),
    (T.CARD_ASSOCIATION, {'asset-001', 'asset-002'}),
    (T.MOLECULAR_ANALYSIS, {'asset-005'}),
    (T.FUNCTION_MOLECULE, {'asset-006', 'asset-008'}),
    (T.FUNCTION_ORDER, {'asset-001', 'asset-002', 'asset-003', 'asset-004'}),
])
def test_assets_referenciados(tipo, esperado):
    assert validar(tipo).assets_referenciados() == esperado


def test_regioes_referenciadas_da_analise_molecular():
    assert validar(T.MOLECULAR_ANALYSIS).regioes_referenciadas() == {'asset-005': {'grupo-oh'}}
