from datetime import datetime
from sqlmodel import Field, SQLModel
from src.Models.base_models import TimestampMixin
from uuid import UUID

class Motorista(TimestampMixin, table=True):
    __tablename__ = "motorista"

    id: UUID = Field(primary_key=True, index=True)
    cnh_numero: str = Field(max_length=20, nullable=False)
    cnh_categoria: str = Field(max_length=5, nullable=False)
    cnh_validade: datetime = Field(nullable=False)
    status: str = Field(default="ATIVA", max_length=20) # 'ATIVA', 'PENDENTE', 'BLOQUEADO', 'SUSPENSO'
