from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session
from src.Dtos.ViagemDto import ViagemCreate, ViagemUpdate, ViagemResponse, DespesaCreate, DespesaResponse
from src.Services import ViagensService

router = APIRouter(prefix="/viagens", tags=["Viagens"])

@router.post("", response_model=ViagemResponse, status_code=status.HTTP_201_CREATED)
async def route_create_viagem(
    data: ViagemCreate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Cadastra uma nova viagem operacional no tenant.
    Valida a existência do veículo e do motorista vinculados.
    """
    viagem = await ViagensService.create_viagem(session, data)
    return ViagemResponse.model_validate(viagem)

@router.get("", response_model=List[ViagemResponse])
async def route_get_viagens(
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna a lista de todas as viagens cadastradas no tenant.
    """
    viagens = await ViagensService.get_viagens(session)
    return [ViagemResponse.model_validate(v) for v in viagens]

@router.get("/{viagem_id}", response_model=ViagemResponse)
async def route_get_viagem_by_id(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna os detalhes de uma viagem específica pelo ID.
    """
    viagem = await ViagensService.get_viagem_by_id(session, viagem_id)
    return ViagemResponse.model_validate(viagem)

@router.put("/{viagem_id}", response_model=ViagemResponse)
async def route_update_viagem(
    viagem_id: UUID,
    data: ViagemUpdate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Atualiza as informações de uma viagem (ex: registrar km_final, alterar status ou registrar data_chegada).
    """
    viagem = await ViagensService.update_viagem(session, viagem_id, data)
    return ViagemResponse.model_validate(viagem)

@router.delete("/{viagem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_viagem(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Remove uma viagem cadastrada no tenant.
    """
    await ViagensService.delete_viagem(session, viagem_id)

@router.post("/{viagem_id}/despesas", response_model=DespesaResponse, status_code=status.HTTP_201_CREATED)
async def route_launch_despesa(
    viagem_id: UUID,
    data: DespesaCreate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Lança uma nova despesa vinculada a uma viagem existente no tenant.
    """
    despesa = await ViagensService.launch_despesa(session, viagem_id, data)
    return DespesaResponse.model_validate(despesa)

@router.get("/{viagem_id}/despesas", response_model=List[DespesaResponse])
async def route_get_despesas(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna todas as despesas lançadas para uma viagem.
    """
    despesas = await ViagensService.get_despesas_by_viagem(session, viagem_id)
    return [DespesaResponse.model_validate(d) for d in despesas]
