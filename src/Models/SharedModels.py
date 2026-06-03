import uuid
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin, TimestampMixin

class Endereco(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "endereco"
    __table_args__ = {"schema": "public"}

    cep: str = Field(max_length=10, nullable=False)
    logradouro: str = Field(max_length=255, nullable=False)
    numero: str = Field(max_length=20, nullable=False)
    complemento: Optional[str] = Field(default=None, max_length=100)
    bairro: str = Field(max_length=100, nullable=False)
    cidade: str = Field(max_length=100, nullable=False)
    estado: str = Field(max_length=2, nullable=False)
    codigo_ibge: Optional[str] = Field(default=None, max_length=10)
    latitude: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=8)
    longitude: Optional[Decimal] = Field(default=None, max_digits=11, decimal_places=8)

class Pessoa(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "pessoa"
    __table_args__ = {"schema": "public"}

    tipo_pessoa: str = Field(max_length=10, nullable=False) # 'FISICA' ou 'JURIDICA'
    nome_razao_social: str = Field(max_length=255, nullable=False)
    telefone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    
    endereco_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.endereco.id")

class PessoaJuridica(SQLModel, table=True):
    __tablename__ = "pessoa_juridica"
    __table_args__ = {"schema": "public"}

    pessoa_id: uuid.UUID = Field(primary_key=True, foreign_key="public.pessoa.id")
    cnpj: str = Field(max_length=18, nullable=False, unique=True)
    nome_fantasia: Optional[str] = Field(default=None, max_length=255)
    inscricao_estadual: Optional[str] = Field(default=None, max_length=50)

class PessoaFisica(SQLModel, table=True):
    __tablename__ = "pessoa_fisica"
    __table_args__ = {"schema": "public"}

    pessoa_id: uuid.UUID = Field(primary_key=True, foreign_key="public.pessoa.id")
    cpf: str = Field(max_length=14, nullable=False, unique=True)
    rg: Optional[str] = Field(default=None, max_length=20)
    data_nascimento: Optional[datetime] = Field(default=None)

class Transportadora(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "transportadora"
    __table_args__ = {"schema": "public"}

    pessoa_juridica_id: uuid.UUID = Field(nullable=False, unique=True, foreign_key="public.pessoa_juridica.pessoa_id")
    rntrc: str = Field(max_length=20, nullable=False)
    status_conta: str = Field(default="ATIVA", max_length=20)
