"""Serviço de questões: regras de negócio do banco de questões.

Permissões por origem (impostas aqui, não na tela):
| Operação | Base | Local | Remota            |
|----------|------|-------|-------------------|
| Consultar| sim  | sim   | sim               |
| Criar    | não  | sim   | não (vem do site) |
| Editar   | não  | sim   | não               |
| Remover  | não  | sim   | sim (cópia local) |

Ao salvar, o serviço valida:
1. dados gerais (minijogo, dificuldade, enunciado, tags, fonte);
2. payload com o schema do minijogo;
3. se os SVGs usados existem e se as regiões destacadas existem dentro deles.

Observação: as funções daqui devolvem a questão COMPLETA (com gabarito), para
a tela de gestão. A versão para a partida (sem gabarito) fica no módulo game/.
"""
from __future__ import annotations

from typing import Any

from pydantic import Field, ValidationError

from backend.database.conexao import sessao
from backend.database.models import Question
from backend.questoes import repositorio
from backend.questoes.assets import apagar_arquivos, caminho_do_arquivo, ler_svg, serializar_asset
from backend.questoes.erros import DadosInvalidos, NaoEncontrado, OperacaoNaoPermitida, traduzir_erros
from backend.questoes.schemas import PayloadBase, validar_payload
from backend.questoes.schemas.base import Esquema, TextoCurto
from backend.questoes.schemas.questao import DadosQuestao
from backend.questoes.tipos import (
    NOMES_DIFICULDADES,
    NOMES_MINIJOGOS,
    NOMES_ORIGENS,
    Difficulty,
    MinigameType,
    SourceType,
)

MENSAGENS_EDICAO = {
    SourceType.BASE: 'Questões-base não podem ser editadas',
    SourceType.REMOTE: 'Questões baixadas do site não podem ser editadas',
}


class FiltrosQuestoes(Esquema):
    minigame_type: MinigameType | None = None
    difficulty: Difficulty | None = None
    source_type: SourceType | None = None
    tag: TextoCurto | None = None
    busca: TextoCurto | None = None
    limite: int = Field(default=50, ge=1, le=200)
    deslocamento: int = Field(default=0, ge=0)


# --- Serialização -------------------------------------------------------------


def permissoes(source_type: str) -> dict:
    return {
        'edit': source_type == SourceType.LOCAL,
        'delete': source_type in (SourceType.LOCAL, SourceType.REMOTE),
    }


def serializar_questao(q: Question, *, completa: bool = True) -> dict:
    """Converte a questão em dicionário simples (pronto para JSON)."""
    dados = {
        'id': q.id,
        'minigame_type': q.minigame_type,
        'minigame_name': NOMES_MINIJOGOS[MinigameType(q.minigame_type)],
        'difficulty': q.difficulty,
        'difficulty_name': NOMES_DIFICULDADES[Difficulty(q.difficulty)],
        'source_type': q.source_type,
        'statement': q.statement,
        'explanation': q.explanation,
        'tags': sorted(t.name for t in q.tags),
        'source': None if q.source is None else {
            campo: getattr(q.source, campo) for campo in repositorio.CAMPOS_FONTE
        },
        'status': q.status,
        'created_at': q.created_at.isoformat() if q.created_at else None,
        'updated_at': q.updated_at.isoformat() if q.updated_at else None,
        'permissions': permissoes(q.source_type),
    }
    if completa:
        dados['payload'] = q.payload
        dados['assets'] = {
            link.asset_id: serializar_asset(link.asset, com_conteudo=True) for link in q.asset_links
        }
    return dados


# --- Validação ------------------------------------------------------------------


def _validar_entrada(s, dados: Any) -> tuple[DadosQuestao, PayloadBase]:
    if not isinstance(dados, dict):
        raise DadosInvalidos([{'campo': '', 'mensagem': 'Formato inválido (esperado um objeto)'}])
    try:
        entrada = DadosQuestao.model_validate(dados)
    except ValidationError as erro:
        raise DadosInvalidos(traduzir_erros(erro)) from None
    try:
        payload = validar_payload(entrada.minigame_type, entrada.payload)
    except ValidationError as erro:
        raise DadosInvalidos(traduzir_erros(erro, 'payload')) from None

    referenciados = payload.assets_referenciados()
    encontrados = repositorio.buscar_assets(s, referenciados)
    if faltando := referenciados - set(encontrados):
        raise DadosInvalidos([
            {'campo': 'payload', 'mensagem': f'Imagem "{a}" não encontrada'} for a in sorted(faltando)
        ])

    problemas = []
    for asset_id, regioes in payload.regioes_referenciadas().items():
        ids_svg = ler_svg(encontrados[asset_id]).ids
        for regiao in sorted(regioes - ids_svg):
            problemas.append({
                'campo': 'payload.highlight.region_id',
                'mensagem': f'A região "{regiao}" não existe na imagem "{asset_id}"',
            })
    if problemas:
        raise DadosInvalidos(problemas)
    return entrada, payload


def _aplicar(s, q: Question, entrada: DadosQuestao, payload: PayloadBase) -> None:
    q.minigame_type = entrada.minigame_type.value
    q.difficulty = int(entrada.difficulty)
    q.statement = entrada.statement
    q.explanation = entrada.explanation
    # dicionário NOVO: garante que o SQLAlchemy perceba a alteração do JSON
    q.payload = payload.model_dump(mode='json', exclude_none=True)
    q.tags = repositorio.obter_ou_criar_tags(s, entrada.tags)
    repositorio.sincronizar_assets(q, payload.assets_referenciados())
    _, fonte_antiga = repositorio.aplicar_fonte(s, q, entrada.source)
    s.flush()
    repositorio.remover_fonte_se_orfa(s, fonte_antiga)


def _obter_ou_erro(s, questao_id: Any) -> Question:
    q = repositorio.obter_questao(s, questao_id) if isinstance(questao_id, str) else None
    if q is None:
        raise NaoEncontrado('Questão não encontrada')
    return q


# --- Operações ------------------------------------------------------------------


def obter_metadados() -> dict:
    """Opções para filtros e formulários da tela."""
    return {
        'minigames': [{'value': t.value, 'name': NOMES_MINIJOGOS[t]} for t in MinigameType],
        'difficulties': [{'value': int(d), 'name': NOMES_DIFICULDADES[d]} for d in Difficulty],
        'source_types': [
            {'value': o.value, 'name': NOMES_ORIGENS[o], 'can_create': o == SourceType.LOCAL, **permissoes(o)}
            for o in SourceType
        ],
    }


def listar_questoes(filtros: dict | None = None) -> dict:
    try:
        f = FiltrosQuestoes.model_validate(filtros or {})
    except ValidationError as erro:
        raise DadosInvalidos(traduzir_erros(erro, 'filtros')) from None
    with sessao() as s:
        itens, total = repositorio.listar_questoes(
            s,
            minigame_type=f.minigame_type.value if f.minigame_type else None,
            difficulty=int(f.difficulty) if f.difficulty else None,
            source_type=f.source_type.value if f.source_type else None,
            tag=f.tag,
            busca=f.busca,
            limite=f.limite,
            deslocamento=f.deslocamento,
        )
        return {
            'items': [serializar_questao(q, completa=False) for q in itens],
            'total': total,
            'limite': f.limite,
            'deslocamento': f.deslocamento,
        }


def obter_questao(questao_id: str) -> dict:
    with sessao() as s:
        return serializar_questao(_obter_ou_erro(s, questao_id))


def criar_questao_local(dados: dict) -> dict:
    with sessao() as s:
        entrada, payload = _validar_entrada(s, dados)
        q = Question(source_type=SourceType.LOCAL)
        s.add(q)
        _aplicar(s, q, entrada, payload)
        s.flush()
        return serializar_questao(q)


def atualizar_questao_local(questao_id: str, dados: dict) -> dict:
    with sessao() as s:
        q = _obter_ou_erro(s, questao_id)
        if q.source_type != SourceType.LOCAL:
            raise OperacaoNaoPermitida(MENSAGENS_EDICAO[SourceType(q.source_type)])
        entrada, payload = _validar_entrada(s, dados)
        _aplicar(s, q, entrada, payload)
        s.flush()
        return serializar_questao(q)


def remover_questao(questao_id: str) -> dict:
    """Remove uma questão local (definitivo) ou a cópia local de uma remota.

    Imagens locais/remotas que ficarem sem uso são apagadas junto (registro e
    arquivo). Imagens das questões-base nunca são apagadas.
    """
    arquivos = []
    with sessao() as s:
        q = _obter_ou_erro(s, questao_id)
        if q.source_type == SourceType.BASE:
            raise OperacaoNaoPermitida('Questões-base não podem ser removidas')

        candidatos = [link.asset for link in q.asset_links if link.asset.source_type != SourceType.BASE]
        fonte = q.source
        s.delete(q)
        s.flush()

        repositorio.remover_fonte_se_orfa(s, fonte)
        for asset in candidatos:
            if repositorio.contar_usos_asset(s, asset.id) == 0:
                arquivos.append(caminho_do_arquivo(asset))
                s.delete(asset)
    apagar_arquivos(arquivos)
    return {'id': questao_id}
