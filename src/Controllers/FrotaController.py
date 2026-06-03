from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session
from src.Dtos.VeiculoDto import VeiculoCreate, VeiculoUpdate, VeiculoResponse
from src.Services import FrotaService

router = APIRouter(prefix="/frota/caminhoes", tags=["Frota (Veículos)"])

@router.post("", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
async def route_create_veiculo(
    data: VeiculoCreate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Cadastra um novo veículo no tenant.
    Se fornecido o código FIPE, busca dados oficiais automaticamente.
    """
    veiculo = await FrotaService.create_veiculo(session, data)
    return VeiculoResponse.model_validate(veiculo)

@router.get("", response_model=List[VeiculoResponse])
async def route_get_veiculos(
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna a lista de todos os veículos cadastrados no tenant.
    """
    veiculos = await FrotaService.get_veiculos(session)
    return [VeiculoResponse.model_validate(v) for v in veiculos]

@router.get("/{veiculo_id}", response_model=VeiculoResponse)
async def route_get_veiculo_by_id(
    veiculo_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna os detalhes de um veículo específico pelo ID.
    """
    veiculo = await FrotaService.get_veiculo_by_id(session, veiculo_id)
    return VeiculoResponse.model_validate(veiculo)

@router.put("/{veiculo_id}", response_model=VeiculoResponse)
async def route_update_veiculo(
    veiculo_id: UUID,
    data: VeiculoUpdate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Atualiza as informações cadastrais de um veículo do tenant.
    """
    veiculo = await FrotaService.update_veiculo(session, veiculo_id, data)
    return VeiculoResponse.model_validate(veiculo)

@router.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_veiculo(
    veiculo_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Remove um veículo do cadastro do tenant.
    """
    await FrotaService.delete_veiculo(session, veiculo_id)
