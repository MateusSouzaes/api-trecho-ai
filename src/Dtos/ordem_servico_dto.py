from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

class OrdemServicoCreate(BaseModel):
    fornecedor_id: Optional[UUID] = None
    cavalo_id: Optional[UUID] = None
    implemento_id: Optional[UUID] = None
    tipo_manutencao: str = Field(..., max_length=20)  # 'PREVENTIVA', 'CORRETIVA'
    hodometro_veiculo: Optional[int] = Field(None, ge=0)
    valor_total_pecas: Decimal = Field(..., ge=0)
    valor_total_mao_obra: Decimal = Field(..., ge=0)
    data_abertura: datetime

class OrdemServicoResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    numero_os: Optional[int]
    fornecedor_id: Optional[UUID]
    cavalo_id: Optional[UUID]
    implemento_id: Optional[UUID]
    tipo_manutencao: str
    hodometro_veiculo: Optional[int]
    valor_total_pecas: Decimal
    valor_total_mao_obra: Decimal
    data_abertura: datetime

    class Config:
        from_attributes = True
