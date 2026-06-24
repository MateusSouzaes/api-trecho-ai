from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.pneu_dto import PneuCreate, PneuResponse, PneuInstalarRequest, PneuRemoverRequest
from src.services.pneu_service import PneuService

router = APIRouter(prefix="/pneus", tags=["Gestão de Pneus"])

@router.post("", response_model=PneuResponse, status_code=status.HTTP_201_CREATED)
async def create_pneu(
    data: PneuCreate,
    current_user: Usuario = Depends(get_current_user),
    service: PneuService = Depends()
):
    pneu = await service.create_pneu(data, current_user.transportadora_id)
    return pneu

@router.get("", response_model=List[PneuResponse])
async def get_pneus(
    current_user: Usuario = Depends(get_current_user),
    service: PneuService = Depends()
):
    records = await service.get_pneus(current_user.transportadora_id)
    return records

@router.post("/{pneu_id}/instalar", response_model=PneuResponse)
async def instalar_pneu(
    pneu_id: UUID,
    data: PneuInstalarRequest,
    current_user: Usuario = Depends(get_current_user),
    service: PneuService = Depends()
):
    pneu = await service.instalar_pneu(pneu_id, data, current_user.transportadora_id)
    return pneu

@router.post("/{pneu_id}/remover", response_model=PneuResponse)
async def remover_pneu(
    pneu_id: UUID,
    data: PneuRemoverRequest,
    current_user: Usuario = Depends(get_current_user),
    service: PneuService = Depends()
):
    pneu = await service.remover_pneu(pneu_id, data, current_user.transportadora_id)
    return pneu
