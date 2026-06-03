import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin

class Fornecedor(UUIDMixin, table=True):
    __tablename__ = "fornecedor"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    pessoa_id: uuid.UUID = Field(nullable=False, foreign_key="public.pessoa.id")
    categoria: str = Field(max_length=50, nullable=False) # 'POSTO_COMBUSTIVEL', 'OFICINA', 'BORRACHARIA'
    status: str = Field(default="ATIVO", max_length=20)
