import uuid
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin

class Cavalo(UUIDMixin, table=True):
    __tablename__ = "cavalo"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    placa: str = Field(max_length=10, nullable=False, unique=True, index=True)
    renavam: str = Field(max_length=20, nullable=False, unique=True)
    chassi: str = Field(max_length=50, nullable=False)
    marca: Optional[str] = Field(default=None, max_length=50)
    modelo: Optional[str] = Field(default=None, max_length=100)
    quantidade_eixos: int = Field(nullable=False)
    tipo_rodado: str = Field(max_length=50, nullable=False)
    tara_kg: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=3)
    hodometro_atual: int = Field(default=0)
    frota_propria: bool = Field(default=True)
    proprietario_pessoa_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.pessoa.id")
    status_veiculo: str = Field(default="DISPONIVEL", max_length=20)
