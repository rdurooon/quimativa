"""Importação do pacote oficial de questões-base.

Roda ao abrir o aplicativo. É idempotente:
- banco já com a mesma versão do pacote: não faz nada (nem lê os SVGs);
- pacote mais novo: insere o que falta e atualiza o que mudou;
- pacote mais antigo que o instalado: ignora (não "volta" o conteúdo).

Tudo acontece numa única transação: se qualquer item do pacote tiver erro,
nada é gravado e o banco continua como estava.

PENDENTE (documento mestre): o que fazer com questões-base que deixaram de
existir no pacote. Por enquanto elas são MANTIDAS e listadas no resultado.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select

from backend import config
from backend.database.conexao import sessao
from backend.database.metadados import definir_versao_base, obter_versao_base
from backend.database.models import Asset, Question
from backend.database.models.pacote import BASE_PACKAGE_ID
from backend.questoes import repositorio
from backend.questoes.erros import ErroPacoteBase, traduzir_erros
from backend.questoes.schemas.pacote_base import PacoteQuestoesBase
from backend.questoes.svg import SvgInvalido, SvgValidado, validar_svg
from backend.questoes.tipos import SourceType

log = logging.getLogger(__name__)


@dataclass
class ResultadoImportacao:
    status: str  # sem_pacote | ja_atualizado | pacote_mais_antigo | importado
    versao: int | None = None
    versao_anterior: int | None = None
    questoes_inseridas: int = 0
    questoes_atualizadas: int = 0
    assets_inseridos: int = 0
    assets_atualizados: int = 0
    questoes_fora_do_pacote: list[str] = field(default_factory=list)


def carregar_pacote(caminho: Path) -> PacoteQuestoesBase:
    try:
        dados = json.loads(caminho.read_text(encoding='utf-8'))
    except json.JSONDecodeError as erro:
        raise ErroPacoteBase([f'JSON inválido (linha {erro.lineno}, coluna {erro.colno}): {erro.msg}']) from None
    try:
        return PacoteQuestoesBase.model_validate(dados)
    except ValidationError as erro:
        raise ErroPacoteBase([f'{e["campo"]}: {e["mensagem"]}' for e in traduzir_erros(erro)]) from None


def validar_arquivos(pacote: PacoteQuestoesBase, pasta_assets: Path) -> dict[str, SvgValidado]:
    """Lê e valida cada SVG do pacote e as regiões destacadas usadas nas questões."""
    problemas: list[str] = []
    svgs: dict[str, SvgValidado] = {}
    raiz = pasta_assets.resolve()

    for asset in pacote.assets:
        caminho = (raiz / asset.file).resolve()
        if raiz not in caminho.parents:
            problemas.append(f'Asset "{asset.id}": caminho fora da pasta de assets')
            continue
        if not caminho.is_file():
            problemas.append(f'Asset "{asset.id}": arquivo não encontrado ({asset.file})')
            continue
        try:
            svgs[asset.id] = validar_svg(caminho.read_bytes())
        except SvgInvalido as erro:
            problemas.append(f'Asset "{asset.id}" ({asset.file}): {erro}')

    for q in pacote.questions:
        for asset_id, regioes in q.payload_validado.regioes_referenciadas().items():
            if asset_id in svgs and (faltando := regioes - svgs[asset_id].ids):
                problemas.append(
                    f'Questão {q.id}: região(ões) {", ".join(sorted(faltando))} '
                    f'não existe(m) no SVG "{asset_id}"'
                )

    if problemas:
        raise ErroPacoteBase(problemas)
    return svgs


def importar_pacote_base(
    caminho_pacote: Path | None = None,
    pasta_assets: Path | None = None,
    *,
    forcar: bool = False,
) -> ResultadoImportacao:
    """Importa o pacote de questões-base. Levanta ErroPacoteBase se houver problemas."""
    caminho = caminho_pacote or config.PACOTE_BASE_PATH
    pasta = pasta_assets or config.ASSETS_BASE_DIR

    if not caminho.exists():
        log.info('Nenhum pacote de questões-base encontrado em %s', caminho)
        return ResultadoImportacao(status='sem_pacote')

    pacote = carregar_pacote(caminho)

    with sessao() as s:
        instalada = obter_versao_base(s)
    if not forcar and instalada is not None:
        if pacote.version == instalada:
            return ResultadoImportacao(status='ja_atualizado', versao=instalada, versao_anterior=instalada)
        if pacote.version < instalada:
            log.warning('Pacote base (v%s) é mais antigo que o instalado (v%s); ignorado',
                        pacote.version, instalada)
            return ResultadoImportacao(status='pacote_mais_antigo', versao=instalada,
                                       versao_anterior=instalada)

    svgs = validar_arquivos(pacote, pasta)
    resultado = ResultadoImportacao(status='importado', versao=pacote.version, versao_anterior=instalada)

    with sessao() as s:
        _importar_assets(s, pacote, svgs, resultado)
        s.flush()
        _importar_questoes(s, pacote, resultado)

        ids_pacote = {str(q.id) for q in pacote.questions}
        resultado.questoes_fora_do_pacote = sorted(
            set(s.scalars(select(Question.id).where(Question.source_type == SourceType.BASE))) - ids_pacote
        )
        definir_versao_base(s, pacote.version)

    log.info('Pacote base v%s importado: %s', pacote.version, resultado)
    if resultado.questoes_fora_do_pacote:
        log.warning('Questões-base que não estão mais no pacote (mantidas): %s',
                    ', '.join(resultado.questoes_fora_do_pacote))
    return resultado


def _importar_assets(s, pacote: PacoteQuestoesBase, svgs: dict[str, SvgValidado],
                     resultado: ResultadoImportacao) -> None:
    problemas = []
    for item in pacote.assets:
        valores = {'file_path': item.file, 'name': item.name, 'checksum': svgs[item.id].checksum}
        asset = s.get(Asset, item.id)
        if asset is None:
            s.add(Asset(id=item.id, source_type=SourceType.BASE, **valores))
            resultado.assets_inseridos += 1
        elif asset.source_type != SourceType.BASE:
            problemas.append(f'Asset "{item.id}" já existe com origem "{asset.source_type}"')
        elif any(getattr(asset, k) != v for k, v in valores.items()):
            for k, v in valores.items():
                setattr(asset, k, v)
            resultado.assets_atualizados += 1
    if problemas:
        raise ErroPacoteBase(problemas)


def _importar_questoes(s, pacote: PacoteQuestoesBase, resultado: ResultadoImportacao) -> None:
    problemas = []
    for item in pacote.questions:
        valores = {
            'minigame_type': item.minigame_type.value,
            'difficulty': int(item.difficulty),
            'statement': item.statement,
            'payload': item.payload,
            'explanation': item.explanation,
            'package_id': BASE_PACKAGE_ID,
        }
        q = s.get(Question, str(item.id))
        if q is None:
            q = Question(id=str(item.id), source_type=SourceType.BASE, **valores)
            s.add(q)
            nova = True
            mudou = True
        elif q.source_type != SourceType.BASE:
            problemas.append(f'Questão {item.id} já existe com origem "{q.source_type}"')
            continue
        else:
            nova = False
            mudou = any(getattr(q, k) != v for k, v in valores.items())
            for k, v in valores.items():
                setattr(q, k, v)

        tags = repositorio.obter_ou_criar_tags(s, item.tags)
        if {t.name for t in q.tags} != {t.name for t in tags}:
            q.tags = tags
            mudou = True

        mudou |= repositorio.sincronizar_assets(q, item.payload_validado.assets_referenciados())

        fonte_mudou, fonte_antiga = repositorio.aplicar_fonte(s, q, item.source)
        mudou |= fonte_mudou
        if fonte_antiga is not None:
            s.flush()
            repositorio.remover_fonte_se_orfa(s, fonte_antiga)

        if nova:
            resultado.questoes_inseridas += 1
        elif mudou:
            resultado.questoes_atualizadas += 1
    if problemas:
        raise ErroPacoteBase(problemas)
