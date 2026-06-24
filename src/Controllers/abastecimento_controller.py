from fastapi import APIRouter, Depends, status
from typing import List

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.abastecimento_dto import AbastecimentoCreate, AbastecimentoResponse
from src.services.abastecimento_service import AbastecimentoService

router = APIRouter(prefix="/abastecimentos", tags=["Abastecimentos"])

@router.post("", response_model=AbastecimentoResponse, status_code=status.HTTP_201_CREATED)
async def create_abastecimento(
    data: AbastecimentoCreate,
    current_user: Usuario = Depends(get_current_user),
    service: AbastecimentoService = Depends()
):
    abast = await service.create_abastecimento(data, current_user.transportadora_id)
    return abast

@router.get("", response_model=List[AbastecimentoResponse])
async def get_abastecimentos(
    current_user: Usuario = Depends(get_current_user),
    service: AbastecimentoService = Depends()
):
    records = await service.get_abastecimentos(current_user.transportadora_id)
    return records
