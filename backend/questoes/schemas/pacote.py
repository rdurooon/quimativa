"""Dados de entrada para criar um pacote local."""
from backend.questoes.schemas.base import Esquema, TextoCurto


class DadosPacote(Esquema):
    name: TextoCurto
