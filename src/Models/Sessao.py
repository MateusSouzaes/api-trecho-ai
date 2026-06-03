import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin, TimestampMixin

class Sessao(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "sessao"
    __table_args__ = {"schema": "auth"}

    usuario_id: uuid.UUID = Field(nullable=False, foreign_key="auth.usuario.id")
    token: str = Field(nullable=False, max_length=500)
    expires_at: datetime = Field(nullable=False)
