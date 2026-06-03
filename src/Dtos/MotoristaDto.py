from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re

CPF_REGEX = re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")

class MotoristaCreate(BaseModel):
    nome: str = Field(..., max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    cpf: str = Field(..., max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[datetime] = None

    cnh_numero: str = Field(..., max_length=20)
    cnh_categoria: str = Field(..., max_length=5)
    cnh_validade: datetime
    status: Optional[str] = Field("ATIVA", max_length=20)

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        clean_cpf = value.replace(".", "").replace("-", "").strip()
        if not CPF_REGEX.match(value) or len(clean_cpf) != 11:
            raise ValueError("CPF inválido.")
        return clean_cpf

class MotoristaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    cnh_numero: Optional[str] = Field(None, max_length=20)
    cnh_categoria: Optional[str] = Field(None, max_length=5)
    cnh_validade: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)

class MotoristaResponse(BaseModel):
    id: UUID
    nome: str
    telefone: Optional[str]
    email: Optional[str]
    cpf: str
    rg: Optional[str]
    data_nascimento: Optional[datetime]
    cnh_numero: str
    cnh_categoria: str
    cnh_validade: datetime
    status: str

    class Config:
        from_attributes = True
