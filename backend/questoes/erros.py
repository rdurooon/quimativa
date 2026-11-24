"""Erros do banco de questões e tradução das mensagens do Pydantic.

Todo erro "esperado" (dados inválidos, operação proibida, não encontrado) é
uma ErroQuestoes com um `codigo` estável, que o frontend pode usar para
decidir o que mostrar. A mensagem é em português e pode ir direto para a tela.
"""
from __future__ import annotations

from pydantic import ValidationError

# --- Exceções ---------------------------------------------------------------


class ErroQuestoes(Exception):
    codigo = 'erro'

    def __init__(self, mensagem: str, detalhes: list[dict] | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or []

    def para_dict(self) -> dict:
        return {'codigo': self.codigo, 'mensagem': self.mensagem, 'detalhes': self.detalhes}


class DadosInvalidos(ErroQuestoes):
    codigo = 'dados_invalidos'

    def __init__(self, detalhes: list[dict], mensagem: str = 'Dados inválidos'):
        super().__init__(mensagem, detalhes)


class NaoEncontrado(ErroQuestoes):
    codigo = 'nao_encontrado'


class OperacaoNaoPermitida(ErroQuestoes):
    codigo = 'nao_permitido'


class ErroPacoteBase(ErroQuestoes):
    """O pacote oficial de questões-base tem problemas (não foi importado)."""

    codigo = 'pacote_base_invalido'

    def __init__(self, problemas: list[str]):
        super().__init__(
            'Pacote de questões-base inválido',
            [{'campo': '', 'mensagem': p} for p in problemas],
        )
        self.problemas = problemas

    def __str__(self) -> str:
        return 'Pacote de questões-base inválido:\n- ' + '\n- '.join(self.problemas)


# --- Tradução das mensagens do Pydantic -------------------------------------

def _mensagem(erro: dict) -> str:
    tipo = erro['type']
    ctx = erro.get('ctx') or {}

    if tipo in ('value_error', 'assertion_error'):
        return str(ctx.get('error', erro['msg'])).removeprefix('Value error, ')
    if tipo == 'missing':
        return 'Campo obrigatório'
    if tipo == 'extra_forbidden':
        return 'Campo não permitido'
    if tipo == 'string_too_short':
        minimo = ctx.get('min_length', 1)
        return 'Não pode ficar vazio' if minimo == 1 else f'Precisa ter pelo menos {minimo} caracteres'
    if tipo == 'string_too_long':
        return f'Texto muito longo (máximo de {ctx.get("max_length")} caracteres)'
    if tipo == 'too_short':
        return f'Precisa ter pelo menos {ctx.get("min_length")} item(ns)'
    if tipo == 'too_long':
        return f'Pode ter no máximo {ctx.get("max_length")} item(ns)'
    if tipo == 'enum':
        return f'Valor inválido. Opções: {ctx.get("expected")}'
    if tipo in ('int_parsing', 'int_type', 'int_from_float'):
        return 'Precisa ser um número inteiro'
    if tipo in ('greater_than_equal', 'greater_than'):
        return f'Precisa ser no mínimo {ctx.get("ge", ctx.get("gt"))}'
    if tipo in ('less_than_equal', 'less_than'):
        return f'Precisa ser no máximo {ctx.get("le", ctx.get("lt"))}'
    if tipo in ('string_type', 'str_type'):
        return 'Precisa ser um texto'
    if tipo == 'list_type':
        return 'Precisa ser uma lista'
    if tipo in ('dict_type', 'model_type', 'model_attributes_type'):
        return 'Formato inválido (esperado um objeto)'
    if tipo in ('uuid_parsing', 'uuid_type'):
        return 'Identificador inválido (esperado um UUID)'
    return erro['msg']  # tipo não previsto: mantém a mensagem original


def traduzir_erros(erro: ValidationError, prefixo: str = '') -> list[dict]:
    """Converte um ValidationError em [{'campo': 'a.b.0', 'mensagem': '...'}]."""
    resultado = []
    for item in erro.errors(include_url=False):
        partes = [prefixo] if prefixo else []
        partes += [str(p) for p in item['loc']]
        resultado.append({'campo': '.'.join(partes), 'mensagem': _mensagem(item)})
    return resultado
