import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.Models.Veiculo import Veiculo
from src.Models.Motorista import Motorista
from src.Models.Viagem import Viagem
from src.Models.DespesaViagem import DespesaViagem
from src.Dtos.ViagemDto import ViagemCreate, ViagemUpdate, DespesaCreate

logger = logging.getLogger(__name__)

async def create_viagem(session: AsyncSession, data: ViagemCreate) -> Viagem:
    """
    Cria uma nova viagem após validar se o veículo e o motorista existem
    no tenant atual.
    """
    # 1. Validar Veículo
    query_veiculo = select(Veiculo).where(Veiculo.id == data.veiculo_id)
    res_veiculo = await session.execute(query_veiculo)
    if not res_veiculo.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não encontrado ou não pertence a esta transportadora."
        )

    # 2. Validar Motorista
    query_motorista = select(Motorista).where(Motorista.id == data.motorista_id)
    res_motorista = await session.execute(query_motorista)
    if not res_motorista.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Motorista não encontrado ou não pertence a esta transportadora."
        )

    # 3. Criar
    viagem = Viagem(
        veiculo_id=data.veiculo_id,
        motorista_id=data.motorista_id,
        origem_cidade=data.origem_cidade,
        destino_cidade=data.destino_cidade,
        km_inicial=data.km_inicial,
        valor_frete=data.valor_frete,
        status=data.status or "ATIVA",
        data_partida=data.data_partida
    )
    session.add(viagem)
    await session.commit()
    await session.refresh(viagem)
    return viagem

async def get_viagens(session: AsyncSession) -> List[Viagem]:
    """Retorna todas as viagens cadastradas no tenant."""
    query = select(Viagem)
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_viagem_by_id(session: AsyncSession, viagem_id: UUID) -> Viagem:
    """Retorna uma viagem pelo ID."""
    query = select(Viagem).where(Viagem.id == viagem_id)
    result = await session.execute(query)
    viagem = result.scalar_one_or_none()
    if not viagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viagem não encontrada."
        )
    return viagem

async def update_viagem(session: AsyncSession, viagem_id: UUID, data: ViagemUpdate) -> Viagem:
    """Atualiza dados cadastrais de uma viagem."""
    viagem = await get_viagem_by_id(session, viagem_id)
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Validações extras para conclusão de viagem
    if "km_final" in update_data and update_data["km_final"] is not None:
        if update_data["km_final"] < viagem.km_inicial:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Km final não pode ser menor que o Km inicial."
            )

    for key, value in update_data.items():
        setattr(viagem, key, value)
        
    session.add(viagem)
    await session.commit()
    await session.refresh(viagem)
    return viagem

async def delete_viagem(session: AsyncSession, viagem_id: UUID) -> None:
    """Exclui uma viagem do cadastro."""
    viagem = await get_viagem_by_id(session, viagem_id)
    await session.delete(viagem)
    await session.commit()

async def launch_despesa(session: AsyncSession, viagem_id: UUID, data: DespesaCreate) -> DespesaViagem:
    """Lança uma nova despesa vinculada a uma viagem existente no tenant."""
    # Verificar se viagem existe
    await get_viagem_by_id(session, viagem_id)

    despesa = DespesaViagem(
        viagem_id=viagem_id,
        tipo_despesa=data.tipo_despesa.upper(),
        valor=data.valor,
        descricao=data.descricao
    )
    session.add(despesa)
    await session.commit()
    await session.refresh(despesa)
    return despesa

async def get_despesas_by_viagem(session: AsyncSession, viagem_id: UUID) -> List[DespesaViagem]:
    """Retorna todas as despesas vinculadas a uma viagem específica."""
    await get_viagem_by_id(session, viagem_id)
    query = select(DespesaViagem).where(DespesaViagem.viagem_id == viagem_id)
    result = await session.execute(query)
    return list(result.scalars().all())
