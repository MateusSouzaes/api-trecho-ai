from fastapi import APIRouter, Depends, status
from typing import List

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.ordem_servico_dto import OrdemServicoCreate, OrdemServicoResponse
from src.services.ordem_servico_service import OrdemServicoService

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço (Manutenção)"])

@router.post("", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
async def create_ordem_servico(
    data: OrdemServicoCreate,
    current_user: Usuario = Depends(get_current_user),
    service: OrdemServicoService = Depends()
):
    os_rec = await service.create_ordem_servico(data, current_user.transportadora_id)
    return os_rec

@router.get("", response_model=List[OrdemServicoResponse])
async def get_ordens_servico(
    current_user: Usuario = Depends(get_current_user),
    service: OrdemServicoService = Depends()
):
    records = await service.get_ordens_servico(current_user.transportadora_id)
    return records
