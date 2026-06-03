import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.Services.ApiClients import fetch_fipe_by_code
from src.Models.Veiculo import Veiculo
from src.Dtos.VeiculoDto import VeiculoCreate, VeiculoUpdate

logger = logging.getLogger(__name__)

async def check_placa_exists(session: AsyncSession, placa: str) -> bool:
    """Verifica se já existe um veículo cadastrado com a placa informada no tenant atual."""
    query = select(Veiculo).where(Veiculo.placa == placa.upper())
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None

async def create_veiculo(session: AsyncSession, data: VeiculoCreate) -> Veiculo:
    """
    Cria um novo veículo. Se o código FIPE for fornecido, realiza a consulta
    real e preenche/substitui marca e modelo com dados oficiais se encontrados.
    """
    # 1. Verificar duplicidade de placa
    if await check_placa_exists(session, data.placa):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Veículo com placa {data.placa} já cadastrado."
        )

    marca = data.marca
    modelo = data.modelo
    ano_modelo = data.ano_modelo

    # 2. Consultar FIPE se fornecido
    if data.codigo_fipe:
        fipe_data = await fetch_fipe_by_code(data.codigo_fipe)
        if fipe_data:
            logger.info(f"Dados FIPE carregados para {data.codigo_fipe}: {fipe_data}")
            marca = fipe_data.get("brand", data.marca)
            modelo = fipe_data.get("model", data.modelo)
            # Extrair ano numérico da FIPE se possível, ex: "2010 Gasolina" -> 2010
            fipe_year = fipe_data.get("modelYear")
            if fipe_year:
                ano_modelo = int(fipe_year)
        else:
            logger.warning(f"Código FIPE {data.codigo_fipe} não retornou resultados na consulta real.")

    # 3. Salvar
    veiculo = Veiculo(
        placa=data.placa.upper(),
        modelo=modelo,
        marca=marca,
        ano_modelo=ano_modelo,
        capacidade_toneladas=data.capacidade_toneladas,
        status=data.status,
        consumo_medio_kml=data.consumo_medio_kml
    )
    session.add(veiculo)
    await session.commit()
    await session.refresh(veiculo)
    return veiculo

async def get_veiculos(session: AsyncSession) -> List[Veiculo]:
    """Retorna a lista de todos os veículos cadastrados no tenant."""
    query = select(Veiculo)
    result = await session.execute(query)
    return list(result.scalars().all())

async def get_veiculo_by_id(session: AsyncSession, veiculo_id: UUID) -> Veiculo:
    """Busca um veículo pelo ID. Levanta 404 se não encontrado."""
    query = select(Veiculo).where(Veiculo.id == veiculo_id)
    result = await session.execute(query)
    veiculo = result.scalar_one_or_none()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado."
        )
    return veiculo

async def update_veiculo(session: AsyncSession, veiculo_id: UUID, data: VeiculoUpdate) -> Veiculo:
    """Atualiza dados cadastrais de um veículo."""
    veiculo = await get_veiculo_by_id(session, veiculo_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(veiculo, key, value)
        
    session.add(veiculo)
    await session.commit()
    await session.refresh(veiculo)
    return veiculo

async def delete_veiculo(session: AsyncSession, veiculo_id: UUID) -> None:
    """Exclui um veículo do cadastro."""
    veiculo = await get_veiculo_by_id(session, veiculo_id)
    await session.delete(veiculo)
    await session.commit()
