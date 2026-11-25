"""Regras de negócio para pacotes de questões."""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.database.conexao import sessao
from backend.database.models import QuestionPackage
from backend.database.models.pacote import BASE_PACKAGE_ID, BASE_PACKAGE_NAME
from backend.questoes import repositorio
from backend.questoes.erros import (
    DadosInvalidos,
    NaoEncontrado,
    OperacaoNaoPermitida,
    traduzir_erros,
)
from backend.questoes.schemas.base import normalizar
from backend.questoes.schemas.pacote import DadosPacote


def _serializar(pacote: QuestionPackage, quantidade: int) -> dict:
    eh_base = pacote.id == BASE_PACKAGE_ID
    return {
        'id': pacote.id,
        'name': pacote.name,
        'kind': 'base' if eh_base else 'local',
        'question_count': quantidade,
        'permissions': {'delete': not eh_base},
    }


def listar_pacotes() -> list[dict]:
    with sessao() as s:
        return [
            _serializar(pacote, int(quantidade or 0))
            for pacote, quantidade in repositorio.listar_pacotes(s)
        ]


def criar_pacote(dados: Any) -> dict:
    try:
        entrada = DadosPacote.model_validate(dados)
    except ValidationError as erro:
        raise DadosInvalidos(traduzir_erros(erro)) from None

    chave = normalizar(entrada.name)
    try:
        with sessao() as s:
            existente = s.scalar(
                select(QuestionPackage).where(QuestionPackage.name_key == chave)
            )
            if existente is not None:
                raise DadosInvalidos([{
                    'campo': 'name',
                    'mensagem': 'Já existe um pacote com esse nome',
                }])

            pacote = QuestionPackage(name=entrada.name, name_key=chave)
            s.add(pacote)
            s.flush()
            return _serializar(pacote, 0)
    except IntegrityError as erro:
        if 'question_packages.name_key' in str(erro.orig):
            raise DadosInvalidos([{
                'campo': 'name',
                'mensagem': 'Já existe um pacote com esse nome',
            }]) from None
        raise


def remover_pacote(package_id: str) -> dict:
    if not isinstance(package_id, str):
        raise NaoEncontrado('Pacote não encontrado')

    with sessao() as s:
        pacote = s.get(QuestionPackage, package_id)
        if pacote is None:
            raise NaoEncontrado('Pacote não encontrado')
        if pacote.id == BASE_PACKAGE_ID:
            raise OperacaoNaoPermitida(f'O pacote "{BASE_PACKAGE_NAME}" não pode ser removido')

        repositorio.desassociar_questoes_do_pacote(s, pacote.id)
        s.delete(pacote)
        s.flush()
    return {'id': package_id}
