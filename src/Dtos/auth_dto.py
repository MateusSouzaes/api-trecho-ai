from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class TransportadoraRegister(BaseModel):
    cnpj: str = Field(..., max_length=18, description="CNPJ da Transportadora")
    nome_razao_social: str = Field(..., max_length=255, description="Razão Social")
    nome_fantasia: Optional[str] = Field(None, max_length=255)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    telefone: Optional[str] = Field(None, max_length=20)
    
    cep: str = Field(..., max_length=10)
    logradouro: str = Field(..., max_length=255)
    numero: str = Field(..., max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: str = Field(..., max_length=100)
    cidade: str = Field(..., max_length=100)
    estado: str = Field(..., max_length=2)
    
    rntrc: str = Field(..., max_length=20, description="RNTRC da Transportadora")
    
    admin_nome: str = Field(..., max_length=255)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=6, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UsuarioResponse(BaseModel):
    id: UUID
    email: EmailStr
    nome: Optional[str]
    role: str
    transportadora_id: UUID

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
