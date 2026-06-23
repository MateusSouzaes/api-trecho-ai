from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.frota_dto import CavaloCreate, CavaloUpdate, CavaloResponse, ImplementoCreate, ImplementoUpdate, ImplementoResponse
from src.services import FrotaService

router = APIRouter(prefix="/frota", tags=["Frota (Cavalos e Implementos)"])

# --- CAVALOS (CAMPONHÕES - LEGACY PATH COMPATIBLE) ---

@router.post("/caminhoes", response_model=CavaloResponse, status_code=status.HTTP_201_CREATED)
async def route_create_cavalo(
    data: CavaloCreate,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Cadastra um novo cavalo mecânico."""
    cavalo = await frota_service.create_cavalo(data, current_user.transportadora_id)
    return CavaloResponse.model_validate(cavalo)

@router.get("/caminhoes", response_model=List[CavaloResponse])
async def route_get_cavalos(
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Retorna todos os cavalos cadastrados da transportadora."""
    cavalos = await frota_service.get_cavalos(current_user.transportadora_id)
    return [CavaloResponse.model_validate(c) for c in cavalos]

@router.get("/caminhoes/{cavalo_id}", response_model=CavaloResponse)
async def route_get_cavalo_by_id(
    cavalo_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Retorna detalhes de um cavalo mecânico pelo ID."""
    cavalo = await frota_service.get_cavalo_by_id(cavalo_id, current_user.transportadora_id)
    return CavaloResponse.model_validate(cavalo)

@router.put("/caminhoes/{cavalo_id}", response_model=CavaloResponse)
async def route_update_cavalo(
    cavalo_id: UUID,
    data: CavaloUpdate,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Atualiza dados cadastrais de um cavalo mecânico."""
    cavalo = await frota_service.update_cavalo(cavalo_id, data, current_user.transportadora_id)
    return CavaloResponse.model_validate(cavalo)

@router.delete("/caminhoes/{cavalo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_cavalo(
    cavalo_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Remove um cavalo mecânico do cadastro."""
    await frota_service.delete_cavalo(cavalo_id, current_user.transportadora_id)


# --- IMPLEMENTOS ---

@router.post("/implementos", response_model=ImplementoResponse, status_code=status.HTTP_201_CREATED)
async def route_create_implemento(
    data: ImplementoCreate,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Cadastra um novo implemento (reboque/semirreboque)."""
    implemento = await frota_service.create_implemento(data, current_user.transportadora_id)
    return ImplementoResponse.model_validate(implemento)

@router.get("/implementos", response_model=List[ImplementoResponse])
async def route_get_implementos(
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Retorna todos os implementos cadastrados."""
    implementos = await frota_service.get_implementos(current_user.transportadora_id)
    return [ImplementoResponse.model_validate(i) for i in implementos]

@router.get("/implementos/{implemento_id}", response_model=ImplementoResponse)
async def route_get_implemento_by_id(
    implemento_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Retorna detalhes de um implemento pelo ID."""
    implemento = await frota_service.get_implemento_by_id(implemento_id, current_user.transportadora_id)
    return ImplementoResponse.model_validate(implemento)

@router.put("/implementos/{implemento_id}", response_model=ImplementoResponse)
async def route_update_implemento(
    implemento_id: UUID,
    data: ImplementoUpdate,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Atualiza dados cadastrais de um implemento."""
    implemento = await frota_service.update_implemento(implemento_id, data, current_user.transportadora_id)
    return ImplementoResponse.model_validate(implemento)

@router.delete("/implementos/{implemento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_implemento(
    implemento_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    frota_service: FrotaService = Depends()
):
    """Remove um implemento do cadastro."""
    await frota_service.delete_implemento(implemento_id, current_user.transportadora_id)
