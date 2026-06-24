from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional

class AbastecimentoCreate(BaseModel):
    cavalo_id: UUID
    fornecedor_id: UUID
    viagem_id: Optional[UUID] = None
    data_abastecimento: datetime
    hodometro_veiculo: int = Field(..., ge=0)
    tipo_combustivel: Optional[str] = Field("DIESEL", max_length=20)
    quantidade_litros: Decimal = Field(..., gt=0)
    valor_unitario_litro: Decimal = Field(..., gt=0)

class AbastecimentoResponse(BaseModel):
    id: UUID
    transportadora_id: UUID
    cavalo_id: UUID
    fornecedor_id: UUID
    viagem_id: Optional[UUID]
    data_abastecimento: datetime
    hodometro_veiculo: int
    tipo_combustivel: Optional[str]
    quantidade_litros: Decimal
    valor_unitario_litro: Decimal
    valor_total: Decimal

    class Config:
        from_attributes = True
