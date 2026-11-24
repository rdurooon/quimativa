"""Informações do próprio aplicativo guardadas no banco (chave -> valor).

Ex.: versão do pacote de questões-base instalado.
"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, agora_utc


class AppMetadata(Base):
    __tablename__ = 'app_metadata'

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=agora_utc, onupdate=agora_utc)
