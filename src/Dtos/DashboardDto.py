from pydantic import BaseModel
from decimal import Decimal
from typing import List

class AlertaDashboard(BaseModel):
    viagem_id: str
    mensagem: str
    tipo: str # 'CORROSIVO_ALERTA', 'ATENCAO'

class DashboardResponse(BaseModel):
    total_receita: Decimal
    total_despesas: Decimal
    margem_contribuicao: Decimal
    total_viagens: int
    percentual_lucro: Decimal
    alertas: List[AlertaDashboard]
