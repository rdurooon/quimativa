"""Testes de pacotes, associação e origem das questões."""
import pytest

from backend import config
from backend.api import API
from backend.database import conexao
from backend.database.inicializacao import inicializar_banco
from backend.database.models import Question, QuestionPackage
from backend.database.models.pacote import BASE_PACKAGE_ID, BASE_PACKAGE_NAME
from backend.questoes import pacotes, servico
from backend.questoes.erros import DadosInvalidos, NaoEncontrado, OperacaoNaoPermitida
from backend.questoes.importador import importar_pacote_base

EXEMPLO = config.BASE_DIR / 'docs' / 'pacote_base_exemplo'
ID_BASE = '5b0e7c52-3f7e-4d8a-9a51-1c2f4e6b8d01'


@pytest.fixture(autouse=True)
def ambiente(pasta_dados, monkeypatch):
    monkeypatch.setattr(config, 'ASSETS_BASE_DIR', EXEMPLO / 'assets')
    inicializar_banco()
    importar_pacote_base(EXEMPLO / 'pacote_base.json', EXEMPLO / 'assets')


def dados_questao(package_id=None):
    dados = {
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
    }
    if package_id is not None:
        dados['package_id'] = package_id
    return dados


def test_pacote_base_e_listado_sem_duplicacao_e_com_contagem():
    before = pacotes.listar_pacotes()
    inicializar_banco()
    after = pacotes.listar_pacotes()

    assert before == after
    assert before[0] == {
        'id': BASE_PACKAGE_ID,
        'name': BASE_PACKAGE_NAME,
        'kind': 'base',
        'question_count': 6,
        'minigame_types': [
            'identification', 'find_difference', 'card_association',
            'molecular_analysis', 'function_molecule', 'function_order',
        ],
        'difficulties': [1, 2, 3],
        'permissions': {'delete': False},
    }

def test_pacote_local_resume_minijogos_e_dificuldades_presentes():
    pacote = pacotes.criar_pacote({'name': 'Resumo'})
    assert pacote['minigame_types'] == []
    assert pacote['difficulties'] == []

    servico.criar_questao_local(dados_questao(pacote['id']))
    listado = next(p for p in pacotes.listar_pacotes() if p['id'] == pacote['id'])
    assert listado['minigame_types'] == ['identification']
    assert listado['difficulties'] == [1]
    assert listado['question_count'] == 1

def test_criar_pacote_e_rejeitar_nome_duplicado_normalizado():
    criado = pacotes.criar_pacote({'name': '  Química   Orgânica  '})

    assert criado['kind'] == 'local'
    assert criado['permissions'] == {'delete': True}
    assert criado['question_count'] == 0
    with pytest.raises(DadosInvalidos) as erro:
        pacotes.criar_pacote({'name': 'química orgânica'})
    assert erro.value.detalhes == [{
        'campo': 'name',
        'mensagem': 'Já existe um pacote com esse nome',
    }]
    with pytest.raises(DadosInvalidos):
        pacotes.criar_pacote({'name': '   '})


def test_associar_a_pacote_local_preserva_origem_e_retorna_pacote_e_preview():
    pacote = pacotes.criar_pacote({'name': 'Minhas questões'})
    questao = servico.criar_questao_local(dados_questao(pacote['id']))

    assert questao['source_type'] == 'local'
    assert questao['permissions'] == {'edit': True, 'delete': True}
    assert questao['package'] == {'id': pacote['id'], 'name': 'Minhas questões'}

    listada = servico.listar_questoes({'source_type': 'local'})['items'][0]
    assert listada['package'] == questao['package']
    assert listada['preview_asset'] == {'id': 'etanol', 'name': 'Etanol'}
    assert pacotes.listar_pacotes()[1]['question_count'] == 1


def test_associar_questao_ao_pacote_base_promove_origem_e_aplica_permissoes():
    questao = servico.criar_questao_local(dados_questao(BASE_PACKAGE_ID))

    assert questao['source_type'] == 'base'
    assert questao['package'] == {'id': BASE_PACKAGE_ID, 'name': BASE_PACKAGE_NAME}
    assert questao['permissions'] == {'edit': False, 'delete': False}
    with pytest.raises(OperacaoNaoPermitida):
        servico.atualizar_questao_local(questao['id'], dados_questao())
    with pytest.raises(OperacaoNaoPermitida):
        servico.remover_questao(questao['id'])


def test_criar_sem_pacote_permanece_local_e_origem_nao_e_editavel():
    questao = servico.criar_questao_local(dados_questao())
    assert questao['package'] is None
    assert questao['source_type'] == 'local'
    assert questao['permissions'] == {'edit': True, 'delete': True}

    dados = dados_questao()
    dados['source_type'] = 'base'
    with pytest.raises(DadosInvalidos):
        servico.criar_questao_local(dados)


def test_remover_pacote_desassocia_questoes_sem_alterar_seus_dados():
    pacote = pacotes.criar_pacote({'name': 'Temporário'})
    questao = servico.criar_questao_local(dados_questao(pacote['id']))
    payload_original = questao['payload']
    asset_original = questao['assets']['etanol']['id']

    assert pacotes.remover_pacote(pacote['id']) == {'id': pacote['id']}
    preservada = servico.obter_questao(questao['id'])
    assert preservada['package'] is None
    assert preservada['source_type'] == 'local'
    assert preservada['statement'] == questao['statement']
    assert preservada['payload'] == payload_original
    assert preservada['assets']['etanol']['id'] == asset_original
    with conexao.sessao() as s:
        assert s.get(Question, questao['id']) is not None
        assert s.get(QuestionPackage, pacote['id']) is None


def test_pacote_base_nao_pode_ser_removido_e_erros_sao_expostos_na_bridge():
    api = API()
    resposta = api.pacotes_remover(BASE_PACKAGE_ID)
    assert resposta['ok'] is False
    assert resposta['erro']['codigo'] == 'nao_permitido'
    assert api.pacotes_remover('inexistente')['erro']['codigo'] == 'nao_encontrado'
    with pytest.raises(OperacaoNaoPermitida):
        pacotes.remover_pacote(BASE_PACKAGE_ID)


def test_bridge_expoe_criar_listar_e_remover_pacote():
    api = API()
    criado = api.pacotes_criar({'name': 'Pacote via bridge'})
    assert criado['ok'] is True
    assert criado['dados']['name'] == 'Pacote via bridge'
    assert any(p['id'] == criado['dados']['id'] for p in api.pacotes_listar()['dados'])
    assert api.pacotes_remover(criado['dados']['id']) == {
        'ok': True,
        'dados': {'id': criado['dados']['id']},
    }
