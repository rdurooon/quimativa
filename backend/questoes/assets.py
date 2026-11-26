"""Serviço de assets (SVGs): importar, listar, obter e remover.

Permissões:
- base: só leitura (vêm com o software);
- local: o usuário importa e remove (se não estiver em uso);
- remote: futuramente baixados do site; só podem ser removidos.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from sqlalchemy import select

from backend import config
from backend.database.base import novo_id
from backend.database.conexao import sessao
from backend.database.models import Asset
from backend.questoes import repositorio
from backend.questoes.erros import (
    AssetIndisponivel,
    DadosInvalidos,
    NaoEncontrado,
    OperacaoNaoPermitida,
)
from backend.questoes.svg import SvgInvalido, SvgValidado, validar_svg
from backend.questoes.tipos import SourceType

log = logging.getLogger(__name__)


# --- Arquivos -----------------------------------------------------------------


def caminho_do_arquivo(asset: Asset) -> Path:
    """Caminho absoluto do SVG, garantindo que fica dentro da pasta da origem."""
    raiz = config.obter_assets_dir(asset.source_type).resolve()
    caminho = (raiz / asset.file_path).resolve()
    if raiz not in caminho.parents:
        raise OperacaoNaoPermitida(f'Caminho inválido para o asset "{asset.id}"')
    return caminho


def ler_svg(asset: Asset) -> SvgValidado:
    """Lê e valida o SVG de um asset do banco."""
    caminho = caminho_do_arquivo(asset)
    if not caminho.is_file():
        raise AssetIndisponivel(f'Arquivo do asset "{asset.id}" não está disponível')
    try:
        return validar_svg(caminho.read_bytes())
    except SvgInvalido as erro:
        raise AssetIndisponivel(f'Arquivo do asset "{asset.id}" não é um SVG válido: {erro}') from None
    except OSError as erro:
        raise AssetIndisponivel(f'Arquivo do asset "{asset.id}" não está disponível') from erro


def apagar_arquivos(caminhos: list[Path]) -> None:
    for caminho in caminhos:
        try:
            caminho.unlink(missing_ok=True)
        except OSError:
            log.warning('Não foi possível apagar o arquivo %s', caminho, exc_info=True)


# --- Serialização -------------------------------------------------------------


def serializar_asset(asset: Asset, *, usos: int | None = None, com_conteudo: bool = False) -> dict:
    dados = {
        'id': asset.id,
        'name': asset.name,
        'source_type': asset.source_type,
        'asset_type': asset.asset_type,
        'checksum': asset.checksum,
        'created_at': asset.created_at.isoformat() if asset.created_at else None,
    }
    if usos is not None:
        dados['usage_count'] = usos
        dados['permissions'] = {
            'delete': asset.source_type != SourceType.BASE and usos == 0,
        }
    if com_conteudo:
        svg = ler_svg(asset)
        # data_uri: para o frontend usar direto em <img src="...">.
        dados['data_uri'] = 'data:image/svg+xml;base64,' + base64.b64encode(svg.conteudo).decode('ascii')
        # region_ids: ids aceitos em highlight.region_id (a mesma lista que o serviço valida).
        dados['region_ids'] = sorted(svg.ids)
    return dados

# --- Operações ----------------------------------------------------------------


def importar_svg_local(conteudo: str | bytes, nome: str | None = None) -> dict:
    """Valida e guarda um SVG enviado pelo usuário. SVG idêntico já existente é reaproveitado."""
    if not isinstance(conteudo, (str, bytes)):
        raise DadosInvalidos([{'campo': 'conteudo', 'mensagem': 'Precisa ser o texto do arquivo SVG'}])
    try:
        svg = validar_svg(conteudo)
    except SvgInvalido as erro:
        raise DadosInvalidos([{'campo': 'conteudo', 'mensagem': str(erro)}], 'SVG inválido') from None

    nome = ' '.join(nome.split())[:200] if isinstance(nome, str) and nome.strip() else None

    with sessao() as s:
        existente = s.scalars(
            select(Asset).where(Asset.source_type == SourceType.LOCAL, Asset.checksum == svg.checksum)
        ).first()
        if existente is not None:
            return serializar_asset(existente, usos=repositorio.contar_usos_asset(s, existente.id),
                                    com_conteudo=True)

    asset_id = novo_id()
    pasta = config.obter_assets_dir(SourceType.LOCAL)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f'{asset_id}.svg'
    arquivo.write_bytes(svg.conteudo)
    try:
        with sessao() as s:
            asset = Asset(id=asset_id, source_type=SourceType.LOCAL, file_path=arquivo.name,
                          name=nome, checksum=svg.checksum)
            s.add(asset)
            s.flush()
            return serializar_asset(asset, usos=0, com_conteudo=True)
    except Exception:
        apagar_arquivos([arquivo])
        raise


def listar_assets(origem: str | None = None, com_conteudo: bool = False) -> list[dict]:
    if origem is not None and origem not in set(SourceType):
        raise DadosInvalidos([{'campo': 'origem', 'mensagem': 'Origem inválida'}])
    with sessao() as s:
        consulta = select(Asset).order_by(Asset.source_type, Asset.name, Asset.id)
        if origem is not None:
            consulta = consulta.where(Asset.source_type == origem)
        return [
            serializar_asset(a, usos=repositorio.contar_usos_asset(s, a.id), com_conteudo=com_conteudo)
            for a in s.scalars(consulta)
        ]


def obter_asset(asset_id: str) -> dict:
    with sessao() as s:
        asset = s.get(Asset, asset_id) if isinstance(asset_id, str) else None
        if asset is None:
            raise NaoEncontrado('Asset não encontrado')
        return serializar_asset(asset, usos=repositorio.contar_usos_asset(s, asset.id), com_conteudo=True)


def remover_asset(asset_id: str) -> dict:
    with sessao() as s:
        asset = s.get(Asset, asset_id) if isinstance(asset_id, str) else None
        if asset is None:
            raise NaoEncontrado('Asset não encontrado')
        if asset.source_type == SourceType.BASE:
            raise OperacaoNaoPermitida('Imagens das questões-base não podem ser removidas')
        if usos := repositorio.contar_usos_asset(s, asset.id):
            raise OperacaoNaoPermitida(f'Imagem em uso por {usos} questão(ões)')
        arquivo = caminho_do_arquivo(asset)
        s.delete(asset)
    apagar_arquivos([arquivo])
    return {'id': asset_id}
