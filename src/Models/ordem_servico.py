import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin
from sqlalchemy import Column, Integer, Identity

class OrdemServico(UUIDMixin, table=True):
    __tablename__ = "ordem_servico"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    
    numero_os: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), unique=True)
    )
    
    fornecedor_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.fornecedor.id")
    cavalo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.cavalo.id")
    implemento_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.implemento.id")
    
    tipo_manutencao: str = Field(max_length=20, nullable=False) # 'PREVENTIVA', 'CORRETIVA', etc.
    hodometro_veiculo: Optional[int] = Field(default=None)
    
    valor_total_pecas: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    valor_total_mao_obra: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    
    data_abertura: datetime = Field(default_factory=datetime.utcnow, nullable=False)
