from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class ViagemCreate(BaseModel):
    motorista_id: UUID
    cavalo_id: UUID
    endereco_origem_id: UUID
    endereco_destino_id: UUID
    data_inicio: datetime
    hodometro_inicial: int = Field(..., ge=0)
    status_operacional: Optional[str] = Field("PLANEJADA", max_length=30)
    status_financeiro: Optional[str] = Field("PENDENTE", max_length=30)
    implemento_ids: Optional[List[UUID]] = None

class ViagemUpdate(BaseModel):
    data_fim: Optional[datetime] = None
    hodometro_final: Optional[int] = Field(None, ge=0)
    status_operacional: Optional[str] = Field(None, max_length=30)
    status_financeiro: Optional[str] = Field(None, max_length=30)

class ViagemResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    codigo_viagem: Optional[int]
    motorista_id: UUID
    cavalo_id: UUID
    endereco_origem_id: UUID
    endereco_destino_id: UUID
    data_inicio: datetime
    data_fim: Optional[datetime]
    hodometro_inicial: int
    hodometro_final: Optional[int]
    total_km_rodado: Optional[int]
    status_operacional: str
    status_financeiro: str

    class Config:
        from_attributes = True

class DespesaCreate(BaseModel):
    categoria: str = Field(..., max_length=50) # e.g. 'COMBUSTIVEL', 'PEDAGIO', etc.
    valor: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    data_despesa: datetime
    url_comprovante: Optional[str] = Field(None, max_length=500)

class DespesaResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    viagem_id: UUID
    categoria: str
    valor: Decimal
    data_despesa: datetime
    url_comprovante: Optional[str]

    class Config:
        from_attributes = True

class ReceitaCreate(BaseModel):
    cliente_pessoa_id: UUID
    tipo_receita: str = Field(..., max_length=50) # e.g. 'FRETE_VALOR', 'PEDAGIO_REEMBOLSO'
    valor: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    status_pagamento: Optional[str] = Field("A_RECEBER", max_length=30)

class ReceitaResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    viagem_id: UUID
    cliente_pessoa_id: UUID
    tipo_receita: str
    valor: Decimal
    status_pagamento: str

    class Config:
        from_attributes = True
