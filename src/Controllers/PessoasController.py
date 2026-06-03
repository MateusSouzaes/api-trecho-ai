from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session
from src.Dtos.MotoristaDto import MotoristaCreate, MotoristaUpdate, MotoristaResponse
from src.Services import PessoasService

router = APIRouter(prefix="/pessoas/motoristas", tags=["Pessoas (Motoristas)"])

@router.post("", response_model=MotoristaResponse, status_code=status.HTTP_201_CREATED)
async def route_create_motorista(
    data: MotoristaCreate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Cadastra um novo motorista associado ao tenant.
    Armazena dados pessoais na tabela global (public) e CNH/status na tabela do tenant.
    """
    motorista = await PessoasService.create_motorista(session, data)
    return motorista

@router.get("", response_model=List[MotoristaResponse])
async def route_get_motoristas(
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna todos os motoristas cadastrados no tenant com seus respectivos dados físicos.
    """
    motoristas = await PessoasService.get_motoristas(session)
    return motoristas

@router.get("/{motorista_id}", response_model=MotoristaResponse)
async def route_get_motorista_by_id(
    motorista_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna os detalhes de um motorista específico pelo ID.
    """
    motorista = await PessoasService.get_motorista_joined(session, motorista_id)
    return motorista

@router.put("/{motorista_id}", response_model=MotoristaResponse)
async def route_update_motorista(
    motorista_id: UUID,
    data: MotoristaUpdate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Atualiza as informações cadastrais e operacionais de um motorista.
    """
    motorista = await PessoasService.update_motorista(session, motorista_id, data)
    return motorista

@router.delete("/{motorista_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_motorista(
    motorista_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Remove a filiação de um motorista do cadastro local do tenant.
    Preserva registros globais no schema público.
    """
    await PessoasService.delete_motorista(session, motorista_id)
