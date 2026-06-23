import uuid
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin

class Pneu(UUIDMixin, table=True):
    __tablename__ = "pneu"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    numero_fogo: str = Field(max_length=50, nullable=False, unique=True, index=True)
    marca: str = Field(max_length=50, nullable=False)
    dimensao: str = Field(max_length=20, nullable=False)
    status_uso: str = Field(default="ESTOQUE", max_length=20)
    sulco_atual_mm: Decimal = Field(max_digits=4, decimal_places=1, nullable=False)
    quilometragem_acumulada: int = Field(default=0)
    
    cavalo_atual_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.cavalo.id")
    implemento_atual_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.implemento.id")
    
    eixo_atual: Optional[int] = Field(default=None)
    posicao_atual: Optional[str] = Field(default=None, max_length=20)
