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

# Texto de apoio exibido ao escolher o minijogo na criação de questão.
DESCRICOES_MINIJOGOS = {
    MinigameType.IDENTIFICATION: 'Uma molécula com um grupo destacado e quatro alternativas; '
                                 'o jogador escolhe a função orgânica do grupo.',
    MinigameType.FIND_DIFFERENCE: 'Duas moléculas lado a lado; o jogador escolhe a que responde ao enunciado.',
    MinigameType.CARD_ASSOCIATION: 'Quatro cartas com imagem ou texto; o jogador encontra o par correto.',
    MinigameType.MOLECULAR_ANALYSIS: 'Uma molécula com uma região destacada e quatro alternativas; '
                                     'o jogador escolhe a correta.',
    MinigameType.FUNCTION_MOLECULE: 'O enunciado informa uma função orgânica; o jogador escolhe, '
                                    'entre quatro moléculas, a que pertence a ela.',
    MinigameType.FUNCTION_ORDER: 'Quatro moléculas; o jogador as coloca na sequência correta.',
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
