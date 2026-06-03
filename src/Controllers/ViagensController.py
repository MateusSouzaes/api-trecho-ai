from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session, get_current_user
from src.Models.Usuario import Usuario
from src.Dtos.ViagemDto import ViagemCreate, ViagemUpdate, ViagemResponse, DespesaCreate, DespesaResponse, ReceitaCreate, ReceitaResponse
from src.Services import ViagensService

router = APIRouter(prefix="/viagens", tags=["Viagens"])

@router.post("", response_model=ViagemResponse, status_code=status.HTTP_201_CREATED)
async def route_create_viagem(
    data: ViagemCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cadastra uma nova viagem operacional."""
    viagem = await ViagensService.create_viagem(session, data, current_user.transportadora_id)
    return ViagemResponse.model_validate(viagem)

@router.get("", response_model=List[ViagemResponse])
async def route_get_viagens(
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna a lista de todas as viagens cadastradas."""
    viagens = await ViagensService.get_viagens(session, current_user.transportadora_id)
    return [ViagemResponse.model_validate(v) for v in viagens]

@router.get("/{viagem_id}", response_model=ViagemResponse)
async def route_get_viagem_by_id(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna os detalhes de uma viagem específica pelo ID."""
    viagem = await ViagensService.get_viagem_by_id(session, viagem_id, current_user.transportadora_id)
    return ViagemResponse.model_validate(viagem)

@router.put("/{viagem_id}", response_model=ViagemResponse)
async def route_update_viagem(
    viagem_id: UUID,
    data: ViagemUpdate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza as informações de uma viagem."""
    viagem = await ViagensService.update_viagem(session, viagem_id, data, current_user.transportadora_id)
    return ViagemResponse.model_validate(viagem)

@router.delete("/{viagem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_viagem(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove uma viagem cadastrada."""
    await ViagensService.delete_viagem(session, viagem_id, current_user.transportadora_id)


# --- DESPESAS ---

@router.post("/{viagem_id}/despesas", response_model=DespesaResponse, status_code=status.HTTP_201_CREATED)
async def route_launch_despesa(
    viagem_id: UUID,
    data: DespesaCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lança uma nova despesa vinculada a uma viagem."""
    despesa = await ViagensService.launch_despesa(session, viagem_id, data, current_user.transportadora_id)
    return DespesaResponse.model_validate(despesa)

@router.get("/{viagem_id}/despesas", response_model=List[DespesaResponse])
async def route_get_despesas(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna todas as despesas lançadas para uma viagem."""
    despesas = await ViagensService.get_despesas_by_viagem(session, viagem_id, current_user.transportadora_id)
    return [DespesaResponse.model_validate(d) for d in despesas]


# --- RECEITAS ---

@router.post("/{viagem_id}/receitas", response_model=ReceitaResponse, status_code=status.HTTP_201_CREATED)
async def route_launch_receita(
    viagem_id: UUID,
    data: ReceitaCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lança uma nova receita vinculada a uma viagem."""
    receita = await ViagensService.launch_receita(session, viagem_id, data, current_user.transportadora_id)
    return ReceitaResponse.model_validate(receita)

@router.get("/{viagem_id}/receitas", response_model=List[ReceitaResponse])
async def route_get_receitas(
    viagem_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna todas as receitas de uma viagem."""
    receitas = await ViagensService.get_receitas_by_viagem(session, viagem_id, current_user.transportadora_id)
    return [ReceitaResponse.model_validate(r) for r in receitas]
