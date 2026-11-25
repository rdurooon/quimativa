"""Migrações idempotentes de payloads JSON já persistidos."""
from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.database.models import AppMetadata, Asset, Question
from backend.questoes.schemas.molecula_da_funcao import FunctionMoleculePayload
from backend.questoes.erros import traduzir_erros
from backend.questoes.tipos import MinigameType

CHAVE_MIGRACAO_QUAL_MOLECULA = 'function_molecule_payload_v1'


@dataclass(frozen=True)
class ResultadoMigracaoPayloads:
    convertidas: int
    validas: int
    nao_convertidas: list[dict[str, str]]
    ja_aplicada: bool = False


def _erro_validacao(erro: ValidationError) -> str:
    return '; '.join(
        f'{item["campo"]}: {item["mensagem"]}'
        for item in traduzir_erros(erro, 'payload')
    )


def _serializar_resultado(resultado: ResultadoMigracaoPayloads) -> str:
    return json.dumps({
        'convertidas': resultado.convertidas,
        'validas': resultado.validas,
        'nao_convertidas': resultado.nao_convertidas,
    }, ensure_ascii=False, sort_keys=True)


def _resultado_salvo(valor: str) -> ResultadoMigracaoPayloads:
    dados = json.loads(valor)
    return ResultadoMigracaoPayloads(
        convertidas=dados['convertidas'],
        validas=dados['validas'],
        nao_convertidas=dados['nao_convertidas'],
        ja_aplicada=True,
    )


def migrar_payloads_qual_molecula(s: Session) -> ResultadoMigracaoPayloads:
    """Converte somente payloads legados que o schema novo representa sem perda.

    Não faz commit. O chamador deve executar a função dentro de uma transação e
    fazer o commit junto com o relatório idempotente em ``app_metadata``.
    """
    marcador = s.get(AppMetadata, CHAVE_MIGRACAO_QUAL_MOLECULA)
    if marcador is not None:
        return _resultado_salvo(marcador.value)

    convertidas = 0
    validas = 0
    nao_convertidas: list[dict[str, str]] = []
    questoes = s.scalars(
        select(Question)
        .where(Question.minigame_type == MinigameType.FUNCTION_MOLECULE)
        .options(selectinload(Question.asset_links))
    )

    for questao in questoes:
        payload = questao.payload
        if not isinstance(payload, dict):
            nao_convertidas.append({
                'question_id': questao.id,
                'reason': 'payload não é um objeto JSON',
            })
            continue

        ja_novo = 'cards' in payload
        try:
            validado = FunctionMoleculePayload.model_validate(payload)
        except ValidationError as erro:
            nao_convertidas.append({
                'question_id': questao.id,
                'reason': _erro_validacao(erro),
            })
            continue

        asset_ids = validado.assets_referenciados()
        if asset_ids:
            encontrados = set(s.scalars(select(Asset.id).where(Asset.id.in_(asset_ids))))
            ausentes = sorted(asset_ids - encontrados)
            vinculados = {link.asset_id for link in questao.asset_links}
            sem_vinculo = sorted(asset_ids - vinculados)
            if ausentes or sem_vinculo:
                problemas = []
                if ausentes:
                    problemas.append(f'assets não encontrados: {", ".join(ausentes)}')
                if sem_vinculo:
                    problemas.append(f'assets sem relação question_assets: {", ".join(sem_vinculo)}')
                nao_convertidas.append({
                    'question_id': questao.id,
                    'reason': '; '.join(problemas),
                })
                continue

        if ja_novo:
            validas += 1
            continue

        questao.payload = validado.model_dump(mode='json', exclude_none=True)
        convertidas += 1

    resultado = ResultadoMigracaoPayloads(
        convertidas=convertidas,
        validas=validas,
        nao_convertidas=nao_convertidas,
    )
    s.add(AppMetadata(
        key=CHAVE_MIGRACAO_QUAL_MOLECULA,
        value=_serializar_resultado(resultado),
    ))
    return resultado


def migracao_pendente(s: Session) -> bool:
    return s.get(AppMetadata, CHAVE_MIGRACAO_QUAL_MOLECULA) is None


def contar_questoes_qual_molecula(s: Session) -> int:
    return s.execute(
        select(func.count()).select_from(Question).where(
            Question.minigame_type == MinigameType.FUNCTION_MOLECULE
        )
    ).scalar_one()
