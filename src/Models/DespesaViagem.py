from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin
from uuid import UUID

class DespesaViagem(UUIDMixin, table=True):
    __tablename__ = "despesa_viagem"

    viagem_id: UUID = Field(nullable=False, foreign_key="viagem.id")
    tipo_despesa: str = Field(max_length=50, nullable=False) # 'COMBUSTIVEL', 'PEDAGIO', 'ALIMENTACAO', 'MANUTENCAO', 'OUTROS'
    valor: Decimal = Field(max_digits=15, decimal_places=2, nullable=False)
    descricao: Optional[str] = Field(default=None, max_length=255)
    data_lancamento: datetime = Field(default_factory=datetime.utcnow, nullable=False)
