from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal
from uuid import UUID
import re

PLACA_REGEX = re.compile(r"^[A-Z]{3}-?[0-9][A-Z0-9][0-9]{2}$", re.IGNORECASE)

class CavaloCreate(BaseModel):
    placa: str = Field(..., max_length=10)
    renavam: str = Field(..., max_length=20)
    chassi: str = Field(..., max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)
    quantidade_eixos: int = Field(..., gt=0)
    tipo_rodado: str = Field(..., max_length=50)
    tara_kg: Optional[Decimal] = Field(None, gt=0)
    hodometro_atual: int = Field(0, ge=0)
    frota_propria: bool = Field(True)
    proprietario_pessoa_id: Optional[UUID] = None
    status_veiculo: Optional[str] = Field("DISPONIVEL", max_length=20)

    @field_validator("placa")
    @classmethod
    def validate_placa(cls, value: str) -> str:
        clean_placa = value.replace("-", "").strip().upper()
        if not PLACA_REGEX.match(clean_placa):
            raise ValueError("Placa inválida. Deve seguir o formato ABC1234 ou ABC1D23.")
        return clean_placa

class CavaloUpdate(BaseModel):
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)
    quantidade_eixos: Optional[int] = Field(None, gt=0)
    tipo_rodado: Optional[str] = Field(None, max_length=50)
    tara_kg: Optional[Decimal] = Field(None, gt=0)
    hodometro_atual: Optional[int] = Field(None, ge=0)
    status_veiculo: Optional[str] = Field(None, max_length=20)

class CavaloResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    placa: str
    renavam: str
    chassi: str
    marca: Optional[str]
    modelo: Optional[str]
    quantidade_eixos: int
    tipo_rodado: str
    tara_kg: Optional[Decimal]
    hodometro_atual: int
    frota_propria: bool
    proprietario_pessoa_id: Optional[UUID]
    status_veiculo: str

    class Config:
        from_attributes = True


class ImplementoCreate(BaseModel):
    placa: str = Field(..., max_length=10)
    renavam: str = Field(..., max_length=20)
    chassi: str = Field(..., max_length=50)
    tipo_implemento: str = Field(..., max_length=50) # 'SEMIRREBOQUE', 'DOLLY', 'REBOQUE'
    tipo_carroceria: Optional[str] = Field(None, max_length=50)
    quantidade_eixos: int = Field(..., gt=0)
    tara_kg: Decimal = Field(..., gt=0)
    capacidade_carga_kg: Decimal = Field(0, ge=0)
    cubagem_m3: Decimal = Field(0, ge=0)
    quilometragem_acumulada: int = Field(0, ge=0)
    frota_propria: bool = Field(True)
    proprietario_pessoa_id: Optional[UUID] = None
    status_veiculo: Optional[str] = Field("DISPONIVEL", max_length=20)

    @field_validator("placa")
    @classmethod
    def validate_placa(cls, value: str) -> str:
        clean_placa = value.replace("-", "").strip().upper()
        if not PLACA_REGEX.match(clean_placa):
            raise ValueError("Placa inválida.")
        return clean_placa

class ImplementoUpdate(BaseModel):
    tipo_carroceria: Optional[str] = Field(None, max_length=50)
    quantidade_eixos: Optional[int] = Field(None, gt=0)
    tara_kg: Optional[Decimal] = Field(None, gt=0)
    capacidade_carga_kg: Optional[Decimal] = Field(None, ge=0)
    cubagem_m3: Optional[Decimal] = Field(None, ge=0)
    quilometragem_acumulada: Optional[int] = Field(None, ge=0)
    status_veiculo: Optional[str] = Field(None, max_length=20)

class ImplementoResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    placa: str
    renavam: str
    chassi: str
    tipo_implemento: str
    tipo_carroceria: Optional[str]
    quantidade_eixos: int
    tara_kg: Decimal
    capacidade_carga_kg: Decimal
    cubagem_m3: Decimal
    quilometragem_acumulada: int
    frota_propria: bool
    proprietario_pessoa_id: Optional[UUID]
    status_veiculo: str

    class Config:
        from_attributes = True
