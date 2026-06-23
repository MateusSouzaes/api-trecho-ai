import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin
from sqlalchemy import Column, Integer, Identity

class MotoristaPerfil(UUIDMixin, table=True):
    __tablename__ = "motorista_perfil"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    pessoa_fisica_id: uuid.UUID = Field(nullable=False, foreign_key="public.pessoa_fisica.pessoa_id")
    
    codigo_interno: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), unique=True)
    )
    
    cnh_numero: str = Field(max_length=20, nullable=False)
    cnh_categoria: str = Field(max_length=5, nullable=False)
    cnh_validade: datetime = Field(nullable=False)
    cnh_pontos: int = Field(default=0)
    status_operacional: str = Field(default="DISPONIVEL", max_length=20)
