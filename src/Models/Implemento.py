import uuid
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin

class Implemento(UUIDMixin, table=True):
    __tablename__ = "implemento"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    placa: str = Field(max_length=10, nullable=False, unique=True, index=True)
    renavam: str = Field(max_length=20, nullable=False, unique=True)
    chassi: str = Field(max_length=50, nullable=False)
    tipo_implemento: str = Field(max_length=50, nullable=False) # 'SEMIRREBOQUE', 'DOLLY', 'REBOQUE'
    tipo_carroceria: Optional[str] = Field(default=None, max_length=50)
    quantidade_eixos: int = Field(nullable=False)
    tara_kg: Decimal = Field(max_digits=10, decimal_places=3, nullable=False)
    capacidade_carga_kg: Decimal = Field(default=0, max_digits=10, decimal_places=3)
    cubagem_m3: Decimal = Field(default=0, max_digits=10, decimal_places=3)
    quilometragem_acumulada: int = Field(default=0)
    frota_propria: bool = Field(default=True)
    proprietario_pessoa_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.pessoa.id")
    status_veiculo: str = Field(default="DISPONIVEL", max_length=20)
