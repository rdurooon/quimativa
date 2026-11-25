"""Operações de banco das questões (consultas e ajustes de relacionamentos).

Sem regras de permissão aqui: isso fica no serviço (servico.py).
Todas as funções recebem uma sessão aberta e não fazem commit.
"""
from __future__ import annotations

from sqlalchemy import case, func, select, update
from sqlalchemy.orm import Session, selectinload

from backend.database.models import Asset, Question, QuestionAsset, QuestionPackage, QuestionSource, Tag
from backend.database.models.pacote import BASE_PACKAGE_ID
from backend.questoes.schemas.base import normalizar
from backend.questoes.schemas.questao import FonteEntrada

# --- Tags -------------------------------------------------------------------


def _mapa_tags(s: Session) -> dict[str, Tag]:
    return {normalizar(t.name): t for t in s.scalars(select(Tag))}


def obter_ou_criar_tags(s: Session, nomes: list[str]) -> list[Tag]:
    """Reaproveita tags existentes ignorando maiúsculas/espaços ("álcool" = "Álcool")."""
    mapa = _mapa_tags(s)
    tags = []
    for nome in nomes:
        chave = normalizar(nome)
        if chave not in mapa:
            mapa[chave] = Tag(name=' '.join(nome.split()))
            s.add(mapa[chave])
        tags.append(mapa[chave])
    return tags


def buscar_tag(s: Session, nome: str) -> Tag | None:
    return _mapa_tags(s).get(normalizar(nome))


# --- Assets -----------------------------------------------------------------


def buscar_assets(s: Session, ids: set[str]) -> dict[str, Asset]:
    if not ids:
        return {}
    return {a.id: a for a in s.scalars(select(Asset).where(Asset.id.in_(ids)))}


def sincronizar_assets(q: Question, asset_ids: set[str]) -> bool:
    """Deixa a questão ligada exatamente aos assets informados. Devolve se mudou."""
    atuais = {link.asset_id for link in q.asset_links}
    if atuais == asset_ids:
        return False
    q.asset_links = [link for link in q.asset_links if link.asset_id in asset_ids]
    for asset_id in sorted(asset_ids - atuais):
        q.asset_links.append(QuestionAsset(asset_id=asset_id))
    return True


def contar_usos_asset(s: Session, asset_id: str) -> int:
    return s.execute(
        select(func.count()).select_from(QuestionAsset).where(QuestionAsset.asset_id == asset_id)
    ).scalar_one()


# --- Pacotes -----------------------------------------------------------------


def listar_pacotes(s: Session) -> list[tuple[QuestionPackage, int]]:
    consulta = (
        select(QuestionPackage, func.count(Question.id))
        .outerjoin(Question, Question.package_id == QuestionPackage.id)
        .group_by(QuestionPackage.id)
        .order_by(case((QuestionPackage.id == BASE_PACKAGE_ID, 0), else_=1), QuestionPackage.name_key)
    )
    return [(pacote, int(quantidade or 0)) for pacote, quantidade in s.execute(consulta)]


def desassociar_questoes_do_pacote(s: Session, package_id: str) -> None:
    s.execute(
        update(Question).where(Question.package_id == package_id).values(package_id=None)
    )


# --- Fontes -----------------------------------------------------------------

CAMPOS_FONTE = ('name', 'reference', 'license', 'notes')


def _contar_usos_fonte(s: Session, fonte: QuestionSource) -> int:
    return s.execute(
        select(func.count()).select_from(Question).where(Question.source_id == fonte.id)
    ).scalar_one()


def aplicar_fonte(s: Session, q: Question, fonte: FonteEntrada | None) -> tuple[bool, QuestionSource | None]:
    """Atualiza a fonte da questão.

    Devolve (mudou, fonte_antiga_desligada). A fonte desligada deve ser
    removida com remover_fonte_se_orfa() depois de um flush.
    """
    atual = q.source
    if fonte is None:
        if atual is None:
            return False, None
        q.source = None
        return True, atual

    valores = fonte.model_dump()
    if atual is not None and all(getattr(atual, c) == valores[c] for c in CAMPOS_FONTE):
        return False, None

    # Fonte usada só por esta questão: edita no lugar. Compartilhada: cria outra.
    if atual is not None and q.id is not None and _contar_usos_fonte(s, atual) <= 1:
        for campo in CAMPOS_FONTE:
            setattr(atual, campo, valores[campo])
        return True, None

    q.source = QuestionSource(**valores)
    return True, atual


def remover_fonte_se_orfa(s: Session, fonte: QuestionSource | None) -> None:
    if fonte is not None and _contar_usos_fonte(s, fonte) == 0:
        s.delete(fonte)


# --- Consultas de questões --------------------------------------------------


def obter_questao(s: Session, questao_id: str) -> Question | None:
    return s.get(Question, questao_id)


def listar_questoes(
    s: Session,
    *,
    minigame_type: str | None = None,
    difficulty: int | None = None,
    source_type: str | None = None,
    tag: str | None = None,
    busca: str | None = None,
    limite: int = 50,
    deslocamento: int = 0,
) -> tuple[list[Question], int]:
    """Lista questões com filtros. Devolve (questões da página, total sem paginação)."""
    consulta = select(Question)
    if minigame_type is not None:
        consulta = consulta.where(Question.minigame_type == minigame_type)
    if difficulty is not None:
        consulta = consulta.where(Question.difficulty == difficulty)
    if source_type is not None:
        consulta = consulta.where(Question.source_type == source_type)
    if tag is not None:
        encontrada = buscar_tag(s, tag)
        if encontrada is None:
            return [], 0
        consulta = consulta.where(Question.tags.any(Tag.id == encontrada.id))
    if busca:
        consulta = consulta.where(Question.statement.contains(busca, autoescape=True))

    total = s.execute(select(func.count()).select_from(consulta.subquery())).scalar_one()
    pagina = s.scalars(
        consulta.options(
            selectinload(Question.tags),
            selectinload(Question.source),
            selectinload(Question.package),
            selectinload(Question.asset_links).selectinload(QuestionAsset.asset),
        )
        .order_by(Question.created_at.desc(), Question.id)
        .limit(limite)
        .offset(deslocamento)
    ).all()
    return list(pagina), total
