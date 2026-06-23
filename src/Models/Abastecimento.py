import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin
from sqlalchemy import Column, Numeric, Computed

class Abastecimento(UUIDMixin, table=True):
    __tablename__ = "abastecimento"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    cavalo_id: uuid.UUID = Field(nullable=False, foreign_key="public.cavalo.id")
    fornecedor_id: uuid.UUID = Field(nullable=False, foreign_key="public.fornecedor.id")
    viagem_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.viagem.id")
    
    data_abastecimento: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    hodometro_veiculo: int = Field(nullable=False)
    tipo_combustivel: Optional[str] = Field(default=None, max_length=20)
    
    quantidade_litros: Decimal = Field(max_digits=10, decimal_places=3, nullable=False)
    valor_unitario_litro: Decimal = Field(max_digits=10, decimal_places=3, nullable=False)
    
    valor_total: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), Computed("quantidade_litros * valor_unitario_litro", persisted=True))
    )
