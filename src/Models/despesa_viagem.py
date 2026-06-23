import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin

class DespesaViagem(UUIDMixin, table=True):
    __tablename__ = "despesa_viagem"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    viagem_id: uuid.UUID = Field(nullable=False, foreign_key="public.viagem.id")
    categoria: str = Field(max_length=50, nullable=False) # e.g. 'COMBUSTIVEL', 'PEDAGIO', etc.
    valor: Decimal = Field(max_digits=10, decimal_places=2, nullable=False)
    data_despesa: datetime = Field(nullable=False)
    url_comprovante: Optional[str] = Field(default=None, max_length=500)
