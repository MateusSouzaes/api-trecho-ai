from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin, TimestampMixin
from uuid import UUID

class Viagem(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "viagem"

    veiculo_id: UUID = Field(nullable=False, foreign_key="veiculo.id")
    motorista_id: UUID = Field(nullable=False, foreign_key="motorista.id")
    origem_cidade: str = Field(max_length=255, nullable=False)
    destino_cidade: str = Field(max_length=255, nullable=False)
    km_inicial: Decimal = Field(max_digits=10, decimal_places=2, nullable=False)
    km_final: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    valor_frete: Decimal = Field(max_digits=15, decimal_places=2, nullable=False)
    status: str = Field(default="ATIVA", max_length=20) # 'ATIVA', 'PENDENTE', 'BLOQUEADO', 'SUSPENSO'
    data_partida: datetime = Field(nullable=False)
    data_chegada: Optional[datetime] = Field(default=None)
