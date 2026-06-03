import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin
from sqlalchemy import Column, Integer, Identity, Computed

class Viagem(UUIDMixin, table=True):
    __tablename__ = "viagem"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    
    codigo_viagem: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), unique=True)
    )
    
    motorista_id: uuid.UUID = Field(nullable=False, foreign_key="public.motorista_perfil.id")
    cavalo_id: uuid.UUID = Field(nullable=False, foreign_key="public.cavalo.id")
    
    endereco_origem_id: uuid.UUID = Field(nullable=False, foreign_key="public.endereco.id")
    endereco_destino_id: uuid.UUID = Field(nullable=False, foreign_key="public.endereco.id")
    
    data_inicio: datetime = Field(nullable=False)
    data_fim: Optional[datetime] = Field(default=None)
    
    hodometro_inicial: int = Field(nullable=False)
    hodometro_final: Optional[int] = Field(default=None)
    
    total_km_rodado: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, Computed("hodometro_final - hodometro_inicial", persisted=True))
    )
    
    status_operacional: str = Field(default="PLANEJADA", max_length=30)
    status_financeiro: str = Field(default="PENDENTE", max_length=30)
