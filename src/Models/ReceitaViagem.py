import uuid
from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin

class ReceitaViagem(UUIDMixin, table=True):
    __tablename__ = "receita_viagem"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    viagem_id: uuid.UUID = Field(nullable=False, foreign_key="public.viagem.id")
    cliente_pessoa_id: uuid.UUID = Field(nullable=False, foreign_key="public.pessoa.id")
    tipo_receita: str = Field(max_length=50, nullable=False) # e.g. 'FRETE_VALOR', 'PEDAGIO_REEMBOLSO', etc.
    valor: Decimal = Field(max_digits=10, decimal_places=2, nullable=False)
    status_pagamento: str = Field(default="A_RECEBER", max_length=30)
