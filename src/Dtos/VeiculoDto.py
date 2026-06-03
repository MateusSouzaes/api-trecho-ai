from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal
from uuid import UUID
import re

PLACA_REGEX = re.compile(r"^[A-Z]{3}-?[0-9][A-Z0-9][0-9]{2}$", re.IGNORECASE)

class VeiculoCreate(BaseModel):
    placa: str = Field(..., max_length=10, description="Placa do veículo")
    modelo: str = Field(..., max_length=100)
    marca: str = Field(..., max_length=100)
    ano_modelo: int = Field(..., gt=1900)
    capacidade_toneladas: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    status: Optional[str] = Field("ATIVA", max_length=20)
    consumo_medio_kml: Decimal = Field(..., gt=0, max_digits=5, decimal_places=2)
    codigo_fipe: Optional[str] = Field(None, description="Código FIPE para consulta automática")

    @field_validator("placa")
    @classmethod
    def validate_placa(cls, value: str) -> str:
        clean_placa = value.replace("-", "").strip().upper()
        if not PLACA_REGEX.match(clean_placa):
            raise ValueError("Placa inválida. Deve seguir o formato ABC1234 ou ABC1D23.")
        return clean_placa

class VeiculoUpdate(BaseModel):
    modelo: Optional[str] = Field(None, max_length=100)
    marca: Optional[str] = Field(None, max_length=100)
    ano_modelo: Optional[int] = Field(None, gt=1900)
    capacidade_toneladas: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    status: Optional[str] = Field(None, max_length=20)
    consumo_medio_kml: Optional[Decimal] = Field(None, gt=0, max_digits=5, decimal_places=2)

class VeiculoResponse(BaseModel):
    id: UUID
    placa: str
    modelo: str
    marca: str
    ano_modelo: int
    capacidade_toneladas: Decimal
    status: str
    consumo_medio_kml: Decimal

    class Config:
        from_attributes = True
