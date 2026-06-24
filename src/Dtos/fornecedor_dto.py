from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class FornecedorCreate(BaseModel):
    nome_razao_social: str = Field(..., max_length=255)
    cnpj: str = Field(..., max_length=18)
    categoria: str = Field(..., max_length=50)  # 'POSTO_COMBUSTIVEL', 'OFICINA', 'BORRACHARIA'
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)

class FornecedorResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    pessoa_id: UUID
    nome_razao_social: str
    categoria: str
    status: str

    class Config:
        from_attributes = True
