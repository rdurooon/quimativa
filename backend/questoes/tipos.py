"""Tipos fixos do banco de questões.

Os valores abaixo são gravados no banco. Não renomeie um valor existente
sem criar uma migração que converta os registros antigos.
"""
from enum import IntEnum, StrEnum


class MinigameType(StrEnum):
    IDENTIFICATION = 'identification'          # Identificação de função orgânica
    FIND_DIFFERENCE = 'find_difference'        # Encontre a diferença
    CARD_ASSOCIATION = 'card_association'      # Associação de cartas
    MOLECULAR_ANALYSIS = 'molecular_analysis'  # Análise molecular
    FUNCTION_MOLECULE = 'function_molecule'    # Qual molécula pertence à função?
    FUNCTION_ORDER = 'function_order'          # Ordem das funções


class Difficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AssetType(StrEnum):
    SVG = 'svg'  # imagens/estruturas das questões são sempre SVG


class SourceType(StrEnum):
    BASE = 'base'      # vem com o software; não pode ser editada nem removida
    LOCAL = 'local'    # criada pelo usuário; CRUD completo
    REMOTE = 'remote'  # baixada do site (futuro); só pode ser removida


# Nomes exibidos ao usuário
NOMES_MINIJOGOS = {
    MinigameType.IDENTIFICATION: 'Identificação de função orgânica',
    MinigameType.FIND_DIFFERENCE: 'Encontre a diferença',
    MinigameType.CARD_ASSOCIATION: 'Associação de cartas',
    MinigameType.MOLECULAR_ANALYSIS: 'Análise molecular',
    MinigameType.FUNCTION_MOLECULE: 'Qual molécula pertence à função?',
    MinigameType.FUNCTION_ORDER: 'Ordem das funções',
}

NOMES_DIFICULDADES = {
    Difficulty.EASY: 'Fácil',
    Difficulty.MEDIUM: 'Média',
    Difficulty.HARD: 'Difícil',
}

NOMES_ORIGENS = {
    SourceType.BASE: 'Base',
    SourceType.LOCAL: 'Local',
    SourceType.REMOTE: 'Site',
}
