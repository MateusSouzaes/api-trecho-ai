from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin, TimestampMixin

class Veiculo(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "veiculo"

    placa: str = Field(max_length=10, nullable=False, unique=True, index=True)
    modelo: str = Field(max_length=100, nullable=False)
    marca: str = Field(max_length=100, nullable=False)
    ano_modelo: int = Field(nullable=False)
    capacidade_toneladas: Decimal = Field(max_digits=10, decimal_places=2, nullable=False)
    status: str = Field(default="ATIVA", max_length=20) # 'ATIVA', 'PENDENTE', 'BLOQUEADO', 'SUSPENSO'
    consumo_medio_kml: Decimal = Field(max_digits=5, decimal_places=2, nullable=False)
