from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

class PneuCreate(BaseModel):
    numero_fogo: str = Field(..., max_length=50)
    marca: str = Field(..., max_length=50)
    dimensao: str = Field(..., max_length=20)
    sulco_atual_mm: Decimal = Field(..., ge=0)
    status_uso: Optional[str] = Field("ESTOQUE", max_length=20)

class PneuResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    numero_fogo: str
    marca: str
    dimensao: str
    status_uso: str
    sulco_atual_mm: Decimal
    quilometragem_acumulada: int
    cavalo_atual_id: Optional[UUID]
    implemento_atual_id: Optional[UUID]
    eixo_atual: Optional[int]
    posicao_atual: Optional[str]

    class Config:
        from_attributes = True

class PneuInstalarRequest(BaseModel):
    cavalo_id: Optional[UUID] = None
    implemento_id: Optional[UUID] = None
    eixo: int
    posicao: str
    hodometro_instalacao: int
    data_instalacao: datetime

class PneuRemoverRequest(BaseModel):
    hodometro_remocao: int
    data_remocao: datetime
    motivo_remocao: str
    novo_sulco_mm: Decimal
