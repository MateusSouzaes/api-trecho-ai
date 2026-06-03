from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class ViagemCreate(BaseModel):
    veiculo_id: UUID
    motorista_id: UUID
    origem_cidade: str = Field(..., max_length=255)
    destino_cidade: str = Field(..., max_length=255)
    km_inicial: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    valor_frete: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    status: Optional[str] = Field("ATIVA", max_length=20)
    data_partida: datetime

class ViagemUpdate(BaseModel):
    km_final: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    status: Optional[str] = Field(None, max_length=20)
    data_chegada: Optional[datetime] = None

class ViagemResponse(BaseModel):
    id: UUID
    veiculo_id: UUID
    motorista_id: UUID
    origem_cidade: str
    destino_cidade: str
    km_inicial: Decimal
    km_final: Optional[Decimal]
    valor_frete: Decimal
    status: str
    data_partida: datetime
    data_chegada: Optional[datetime]

    class Config:
        from_attributes = True

class DespesaCreate(BaseModel):
    tipo_despesa: str = Field(..., max_length=50)
    valor: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    descricao: Optional[str] = Field(None, max_length=255)

class DespesaResponse(BaseModel):
    id: UUID
    viagem_id: UUID
    tipo_despesa: str
    valor: Decimal
    descricao: Optional[str]
    data_lancamento: datetime

    class Config:
        from_attributes = True
