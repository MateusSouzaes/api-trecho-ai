from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session, get_current_user
from src.Models.Usuario import Usuario
from src.Dtos.MotoristaDto import MotoristaCreate, MotoristaUpdate, MotoristaResponse
from src.Services import PessoasService

router = APIRouter(prefix="/pessoas/motoristas", tags=["Pessoas (Motoristas)"])

@router.post("", response_model=MotoristaResponse, status_code=status.HTTP_201_CREATED)
async def route_create_motorista(
    data: MotoristaCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cadastra um novo motorista associado ao tenant."""
    motorista = await PessoasService.create_motorista(session, data, current_user.transportadora_id)
    return motorista

@router.get("", response_model=List[MotoristaResponse])
async def route_get_motoristas(
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna todos os motoristas cadastrados na transportadora."""
    motoristas = await PessoasService.get_motoristas(session, current_user.transportadora_id)
    return motoristas

@router.get("/{motorista_id}", response_model=MotoristaResponse)
async def route_get_motorista_by_id(
    motorista_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna os detalhes de um motorista específico pelo ID."""
    motorista = await PessoasService.get_motorista_joined(session, motorista_id, current_user.transportadora_id)
    return motorista

@router.put("/{motorista_id}", response_model=MotoristaResponse)
async def route_update_motorista(
    motorista_id: UUID,
    data: MotoristaUpdate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza as informações cadastrais e operacionais de um motorista."""
    motorista = await PessoasService.update_motorista(session, motorista_id, data, current_user.transportadora_id)
    return motorista

@router.delete("/{motorista_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_motorista(
    motorista_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove a filiação de um motorista do cadastro local da transportadora."""
    await PessoasService.delete_motorista(session, motorista_id, current_user.transportadora_id)
