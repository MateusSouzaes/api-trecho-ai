from fastapi import APIRouter, Depends

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.dashboard_dto import DashboardResponse
from src.services import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard / FinOps"])

@router.get("/lucratividade", response_model=DashboardResponse)
async def get_lucratividade_dashboard(
    current_user: Usuario = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """
    Retorna consolidados financeiros de FinOps (Receitas, Despesas, Margens)
    e gera alertas operacionais de viagens de baixo rendimento ou prejuízo.
    """
    dashboard_data = await dashboard_service.get_lucratividade_dashboard(current_user.transportadora_id)
    return dashboard_data
