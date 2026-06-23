from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.motorista_dto import MotoristaCreate, MotoristaUpdate, MotoristaResponse
from src.services import PessoasService

router = APIRouter(prefix="/pessoas/motoristas", tags=["Pessoas (Motoristas)"])

@router.post("", response_model=MotoristaResponse, status_code=status.HTTP_201_CREATED)
async def route_create_motorista(
    data: MotoristaCreate,
    current_user: Usuario = Depends(get_current_user),
    pessoas_service: PessoasService = Depends()
):
    """Cadastra um novo motorista associado ao tenant."""
    motorista = await pessoas_service.create_motorista(data, current_user.transportadora_id)
    return motorista

@router.get("", response_model=List[MotoristaResponse])
async def route_get_motoristas(
    current_user: Usuario = Depends(get_current_user),
    pessoas_service: PessoasService = Depends()
):
    """Retorna todos os motoristas cadastrados na transportadora."""
    motoristas = await pessoas_service.get_motoristas(current_user.transportadora_id)
    return motoristas

@router.get("/{motorista_id}", response_model=MotoristaResponse)
async def route_get_motorista_by_id(
    motorista_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    pessoas_service: PessoasService = Depends()
):
    """Retorna os detalhes de um motorista específico pelo ID."""
    motorista = await pessoas_service.get_motorista_joined(motorista_id, current_user.transportadora_id)
    return motorista

@router.put("/{motorista_id}", response_model=MotoristaResponse)
async def route_update_motorista(
    motorista_id: UUID,
    data: MotoristaUpdate,
    current_user: Usuario = Depends(get_current_user),
    pessoas_service: PessoasService = Depends()
):
    """Atualiza as informações cadastrais e operacionais de um motorista."""
    motorista = await pessoas_service.update_motorista(motorista_id, data, current_user.transportadora_id)
    return motorista

@router.delete("/{motorista_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_motorista(
    motorista_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    pessoas_service: PessoasService = Depends()
):
    """Remove a filiação de um motorista do cadastro local da transportadora."""
    await pessoas_service.delete_motorista(motorista_id, current_user.transportadora_id)
