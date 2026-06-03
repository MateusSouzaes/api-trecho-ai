from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session, get_current_user
from src.Models.Usuario import Usuario
from src.Dtos.FrotaDto import CavaloCreate, CavaloUpdate, CavaloResponse, ImplementoCreate, ImplementoUpdate, ImplementoResponse
from src.Services import FrotaService

router = APIRouter(prefix="/frota", tags=["Frota (Cavalos e Implementos)"])

# --- CAVALOS (CAMPONHÕES - LEGACY PATH COMPATIBLE) ---

@router.post("/caminhoes", response_model=CavaloResponse, status_code=status.HTTP_201_CREATED)
async def route_create_cavalo(
    data: CavaloCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cadastra um novo cavalo mecânico."""
    cavalo = await FrotaService.create_cavalo(session, data, current_user.transportadora_id)
    return CavaloResponse.model_validate(cavalo)

@router.get("/caminhoes", response_model=List[CavaloResponse])
async def route_get_cavalos(
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna todos os cavalos cadastrados da transportadora."""
    cavalos = await FrotaService.get_cavalos(session, current_user.transportadora_id)
    return [CavaloResponse.model_validate(c) for c in cavalos]

@router.get("/caminhoes/{cavalo_id}", response_model=CavaloResponse)
async def route_get_cavalo_by_id(
    cavalo_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna detalhes de um cavalo mecânico pelo ID."""
    cavalo = await FrotaService.get_cavalo_by_id(session, cavalo_id, current_user.transportadora_id)
    return CavaloResponse.model_validate(cavalo)

@router.put("/caminhoes/{cavalo_id}", response_model=CavaloResponse)
async def route_update_cavalo(
    cavalo_id: UUID,
    data: CavaloUpdate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza dados cadastrais de um cavalo mecânico."""
    cavalo = await FrotaService.update_cavalo(session, cavalo_id, data, current_user.transportadora_id)
    return CavaloResponse.model_validate(cavalo)

@router.delete("/caminhoes/{cavalo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_cavalo(
    cavalo_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove um cavalo mecânico do cadastro."""
    await FrotaService.delete_cavalo(session, cavalo_id, current_user.transportadora_id)


# --- IMPLEMENTOS ---

@router.post("/implementos", response_model=ImplementoResponse, status_code=status.HTTP_201_CREATED)
async def route_create_implemento(
    data: ImplementoCreate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cadastra um novo implemento (reboque/semirreboque)."""
    implemento = await FrotaService.create_implemento(session, data, current_user.transportadora_id)
    return ImplementoResponse.model_validate(implemento)

@router.get("/implementos", response_model=List[ImplementoResponse])
async def route_get_implementos(
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna todos os implementos cadastrados."""
    implementos = await FrotaService.get_implementos(session, current_user.transportadora_id)
    return [ImplementoResponse.model_validate(i) for i in implementos]

@router.get("/implementos/{implemento_id}", response_model=ImplementoResponse)
async def route_get_implemento_by_id(
    implemento_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna detalhes de um implemento pelo ID."""
    implemento = await FrotaService.get_implemento_by_id(session, implemento_id, current_user.transportadora_id)
    return ImplementoResponse.model_validate(implemento)

@router.put("/implementos/{implemento_id}", response_model=ImplementoResponse)
async def route_update_implemento(
    implemento_id: UUID,
    data: ImplementoUpdate,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza dados cadastrais de um implemento."""
    implemento = await FrotaService.update_implemento(session, implemento_id, data, current_user.transportadora_id)
    return ImplementoResponse.model_validate(implemento)

@router.delete("/implementos/{implemento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_implemento(
    implemento_id: UUID,
    session: AsyncSession = Depends(get_current_tenant_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove um implemento do cadastro."""
    await FrotaService.delete_implemento(session, implemento_id, current_user.transportadora_id)
