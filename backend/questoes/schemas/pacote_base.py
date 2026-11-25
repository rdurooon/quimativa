"""Formato do pacote de questões-base (arquivo distribuído com o software).

Arquivo: backend/questoes/dados/pacote_base.json
SVGs:    backend/questoes/assets/base/  (caminhos do pacote são relativos a esta pasta)
Exemplo completo: docs/pacote_base_exemplo/

Regras principais:
- cada questão-base tem um ID FIXO (UUID) escrito no arquivo. Assim a mesma
  questão tem o mesmo ID em todos os computadores, a carga não duplica registros
  e as atualizações oficiais sabem qual questão atualizar;
- cada SVG tem um ID fixo e pode ser usado por várias questões;
- `version` aumenta a cada atualização oficial do conteúdo.

Gerar um UUID novo (uma vez, ao criar a questão):
    python -c "import uuid; print(uuid.uuid4())"
"""
from uuid import UUID

from pydantic import Field, PrivateAttr, ValidationError, field_validator, model_validator

from backend.questoes.erros import traduzir_erros
from backend.questoes.schemas import validar_payload
from backend.questoes.schemas.base import Esquema, Identificador, PayloadBase, TextoCurto, repetidos
from backend.questoes.schemas.questao import DadosQuestao
from backend.questoes.svg import validar_caminho_relativo


class AssetBase(Esquema):
    id: Identificador          # ex.: "etanol" (fixo, referenciado nos payloads)
    file: str                  # caminho relativo, ex.: "alcoois/etanol.svg"
    name: TextoCurto | None = None

    @field_validator('file')
    @classmethod
    def _caminho_seguro(cls, valor: str) -> str:
        return validar_caminho_relativo(valor)


class QuestaoBase(DadosQuestao):
    id: UUID
    package_id: None = None

    _payload: PayloadBase = PrivateAttr()

    @model_validator(mode='after')
    def _validar_payload(self):
        try:
            self._payload = validar_payload(self.minigame_type, self.payload)
        except ValidationError as erro:
            resumo = '; '.join(f'{e["campo"]}: {e["mensagem"]}' for e in traduzir_erros(erro, 'payload'))
            raise ValueError(f'payload inválido ({resumo})') from None
        self.payload = self._payload.model_dump(mode='json', exclude_none=True)
        return self

    @property
    def payload_validado(self) -> PayloadBase:
        return self._payload


class PacoteQuestoesBase(Esquema):
    version: int = Field(ge=1)
    assets: list[AssetBase] = []
    questions: list[QuestaoBase]

    @model_validator(mode='after')
    def _consistencia(self):
        if duplicados := repetidos(a.id for a in self.assets):
            raise ValueError(f'IDs de asset repetidos no pacote: {", ".join(duplicados)}')
        if duplicados := repetidos(a.file.lower() for a in self.assets):
            raise ValueError(f'Arquivos de asset repetidos no pacote: {", ".join(duplicados)}')
        if duplicados := repetidos(str(q.id) for q in self.questions):
            raise ValueError(f'IDs de questão repetidos no pacote: {", ".join(duplicados)}')

        ids_assets = {a.id for a in self.assets}
        for q in self.questions:
            if faltando := q.payload_validado.assets_referenciados() - ids_assets:
                raise ValueError(
                    f'Questão {q.id} usa asset(s) não declarado(s) no pacote: {", ".join(sorted(faltando))}'
                )
        return self
