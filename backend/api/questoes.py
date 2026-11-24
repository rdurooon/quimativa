"""Bridge do banco de questões: funções chamadas pelo frontend (Vue).

No JavaScript:  const r = await window.pywebview.api.questoes_listar({ minigame_type: 'identification' })

Toda função devolve um envelope:
    sucesso: { ok: true,  dados: ... }
    erro:    { ok: false, erro: { codigo, mensagem, detalhes: [{ campo, mensagem }] } }

Contrato completo: docs/contrato_bridge_questoes.md
"""
from __future__ import annotations

import functools
import logging

from backend.questoes import assets, servico
from backend.questoes.erros import ErroQuestoes

log = logging.getLogger(__name__)


def endpoint(funcao):
    """Converte o resultado/erro da função no envelope { ok, dados | erro }."""

    @functools.wraps(funcao)
    def envolver(*args, **kwargs):
        try:
            return {'ok': True, 'dados': funcao(*args, **kwargs)}
        except ErroQuestoes as erro:
            return {'ok': False, 'erro': erro.para_dict()}
        except Exception:
            log.exception('Erro inesperado em %s', funcao.__name__)
            return {'ok': False, 'erro': {
                'codigo': 'erro_interno',
                'mensagem': 'Erro inesperado. Consulte o log do aplicativo.',
                'detalhes': [],
            }}

    return envolver


class QuestoesAPI:
    """Métodos de questões expostos em window.pywebview.api.*"""

    # --- Questões ---
    @endpoint
    def questoes_metadados(self):
        return servico.obter_metadados()

    @endpoint
    def questoes_listar(self, filtros=None):
        return servico.listar_questoes(filtros)

    @endpoint
    def questoes_obter(self, questao_id):
        return servico.obter_questao(questao_id)

    @endpoint
    def questoes_criar(self, dados):
        return servico.criar_questao_local(dados)

    @endpoint
    def questoes_atualizar(self, questao_id, dados):
        return servico.atualizar_questao_local(questao_id, dados)

    @endpoint
    def questoes_remover(self, questao_id):
        return servico.remover_questao(questao_id)

    # --- Imagens (SVG) ---
    @endpoint
    def assets_importar_svg(self, conteudo, nome=None):
        return assets.importar_svg_local(conteudo, nome)

    @endpoint
    def assets_listar(self, origem=None, com_conteudo=False):
        return assets.listar_assets(origem, bool(com_conteudo))

    @endpoint
    def assets_obter(self, asset_id):
        return assets.obter_asset(asset_id)

    @endpoint
    def assets_remover(self, asset_id):
        return assets.remover_asset(asset_id)
