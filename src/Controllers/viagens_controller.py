from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.viagem_dto import ViagemCreate, ViagemUpdate, ViagemResponse, DespesaCreate, DespesaResponse, ReceitaCreate, ReceitaResponse
from src.services import ViagensService

router = APIRouter(prefix="/viagens", tags=["Viagens"])

@router.post("", response_model=ViagemResponse, status_code=status.HTTP_201_CREATED)
async def route_create_viagem(
    data: ViagemCreate,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Cadastra uma nova viagem operacional."""
    viagem = await viagens_service.create_viagem(data, current_user.transportadora_id)
    return ViagemResponse.model_validate(viagem)

@router.get("", response_model=List[ViagemResponse])
async def route_get_viagens(
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Retorna a lista de todas as viagens cadastradas."""
    viagens = await viagens_service.get_viagens(current_user.transportadora_id)
    return [ViagemResponse.model_validate(v) for v in viagens]

@router.get("/{viagem_id}", response_model=ViagemResponse)
async def route_get_viagem_by_id(
    viagem_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Retorna os detalhes de uma viagem específica pelo ID."""
    viagem = await viagens_service.get_viagem_by_id(viagem_id, current_user.transportadora_id)
    return ViagemResponse.model_validate(viagem)

@router.put("/{viagem_id}", response_model=ViagemResponse)
async def route_update_viagem(
    viagem_id: UUID,
    data: ViagemUpdate,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Atualiza as informações de uma viagem."""
    viagem = await viagens_service.update_viagem(viagem_id, data, current_user.transportadora_id)
    return ViagemResponse.model_validate(viagem)

@router.delete("/{viagem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def route_delete_viagem(
    viagem_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Remove uma viagem cadastrada."""
    await viagens_service.delete_viagem(viagem_id, current_user.transportadora_id)


# --- DESPESAS ---

@router.post("/{viagem_id}/despesas", response_model=DespesaResponse, status_code=status.HTTP_201_CREATED)
async def route_launch_despesa(
    viagem_id: UUID,
    data: DespesaCreate,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Lança uma nova despesa vinculada a uma viagem."""
    despesa = await viagens_service.launch_despesa(viagem_id, data, current_user.transportadora_id)
    return DespesaResponse.model_validate(despesa)

@router.get("/{viagem_id}/despesas", response_model=List[DespesaResponse])
async def route_get_despesas(
    viagem_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Retorna todas as despesas lançadas para uma viagem."""
    despesas = await viagens_service.get_despesas_by_viagem(viagem_id, current_user.transportadora_id)
    return [DespesaResponse.model_validate(d) for d in despesas]


# --- RECEITAS ---

@router.post("/{viagem_id}/receitas", response_model=ReceitaResponse, status_code=status.HTTP_201_CREATED)
async def route_launch_receita(
    viagem_id: UUID,
    data: ReceitaCreate,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Lança uma nova receita vinculada a uma viagem."""
    receita = await viagens_service.launch_receita(viagem_id, data, current_user.transportadora_id)
    return ReceitaResponse.model_validate(receita)

@router.get("/{viagem_id}/receitas", response_model=List[ReceitaResponse])
async def route_get_receitas(
    viagem_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    viagens_service: ViagensService = Depends()
):
    """Retorna todas as receitas de uma viagem."""
    receitas = await viagens_service.get_receitas_by_viagem(viagem_id, current_user.transportadora_id)
    return [ReceitaResponse.model_validate(r) for r in receitas]
