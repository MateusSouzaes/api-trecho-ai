from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.DataContexts.DatabaseContext import get_current_tenant_session, get_current_user
from src.Models.Usuario import Usuario
from src.Dtos.DashboardDto import DashboardResponse
from src.Services import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard / FinOps"])

@router.get("/lucratividade", response_model=DashboardResponse)
async def get_lucratividade_dashboard(
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna consolidados financeiros de FinOps (Receitas, Despesas, Margens)
    e gera alertas operacionais de viagens de baixo rendimento ou prejuízo.
    """
    dashboard_data = await DashboardService.get_lucratividade_dashboard(session, current_user.transportadora_id)
    return dashboard_data
