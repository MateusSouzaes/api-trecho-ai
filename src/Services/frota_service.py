from src.data_contexts.database_context import get_current_tenant_session
import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status

from src.services.api_clients import fetch_fipe_by_code
from src.models.cavalo import Cavalo
from src.models.implemento import Implemento
from src.dtos.frota_dto import CavaloCreate, CavaloUpdate, ImplementoCreate, ImplementoUpdate

logger = logging.getLogger(__name__)

# --- CAVALO SERVICES ---



class FrotaService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def check_cavalo_placa_exists(self, placa: str, transportadora_id: UUID) -> bool:
        """Verifica se já existe um cavalo cadastrado com a placa informada."""
        query = select(Cavalo).where(
            Cavalo.placa == placa.upper(),
            Cavalo.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_cavalo(self, data: CavaloCreate, transportadora_id: UUID) -> Cavalo:
        """Cria um novo cavalo no banco."""
        if await self.check_cavalo_placa_exists( data.placa, transportadora_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cavalo com placa {data.placa} já cadastrado."
            )

        marca = data.marca
        modelo = data.modelo

        # 3. Salvar
        cavalo = Cavalo(
            transportadora_id=transportadora_id,
            placa=data.placa.upper(),
            renavam=data.renavam,
            chassi=data.chassi,
            marca=marca,
            modelo=modelo,
            quantidade_eixos=data.quantidade_eixos,
            tipo_rodado=data.tipo_rodado,
            tara_kg=data.tara_kg,
            hodometro_atual=data.hodometro_atual,
            frota_propria=data.frota_propria,
            proprietario_pessoa_id=data.proprietario_pessoa_id,
            status_veiculo=data.status_veiculo or "DISPONIVEL"
        )
        self.session.add(cavalo)
        await self.session.commit()
        await self.session.refresh(cavalo)
        return cavalo

    async def get_cavalos(self, transportadora_id: UUID) -> List[Cavalo]:
        """Retorna a lista de todos os cavalos cadastrados da transportadora."""
        query = select(Cavalo).where(Cavalo.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_cavalo_by_id(self, cavalo_id: UUID, transportadora_id: UUID) -> Cavalo:
        """Busca um cavalo pelo ID. Levanta 404 se não encontrado."""
        query = select(Cavalo).where(
            Cavalo.id == cavalo_id,
            Cavalo.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        cavalo = result.scalar_one_or_none()
        if not cavalo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cavalo mecânico não encontrado."
            )
        return cavalo

    async def update_cavalo(self, cavalo_id: UUID, data: CavaloUpdate, transportadora_id: UUID) -> Cavalo:
        """Atualiza dados cadastrais de um cavalo."""
        cavalo = await self.get_cavalo_by_id( cavalo_id, transportadora_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cavalo, key, value)

        self.session.add(cavalo)
        await self.session.commit()
        await self.session.refresh(cavalo)
        return cavalo

    async def delete_cavalo(self, cavalo_id: UUID, transportadora_id: UUID) -> None:
        """Exclui um cavalo do cadastro."""
        cavalo = await self.get_cavalo_by_id( cavalo_id, transportadora_id)
        await self.session.delete(cavalo)
        await self.session.commit()


    # --- IMPLEMENTO SERVICES ---

    async def check_implemento_placa_exists(self, placa: str, transportadora_id: UUID) -> bool:
        """Verifica se já existe um implemento cadastrado com a placa informada."""
        query = select(Implemento).where(
            Implemento.placa == placa.upper(),
            Implemento.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_implemento(self, data: ImplementoCreate, transportadora_id: UUID) -> Implemento:
        """Cria um novo implemento no banco."""
        if await self.check_implemento_placa_exists( data.placa, transportadora_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Implemento com placa {data.placa} já cadastrado."
            )

        # Salvar
        implemento = Implemento(
            transportadora_id=transportadora_id,
            placa=data.placa.upper(),
            renavam=data.renavam,
            chassi=data.chassi,
            tipo_implemento=data.tipo_implemento,
            tipo_carroceria=data.tipo_carroceria,
            quantidade_eixos=data.quantidade_eixos,
            tara_kg=data.tara_kg,
            capacidade_carga_kg=data.capacidade_carga_kg,
            cubagem_m3=data.cubagem_m3,
            quilometragem_acumulada=data.quilometragem_acumulada,
            frota_propria=data.frota_propria,
            proprietario_pessoa_id=data.proprietario_pessoa_id,
            status_veiculo=data.status_veiculo or "DISPONIVEL"
        )
        self.session.add(implemento)
        await self.session.commit()
        await self.session.refresh(implemento)
        return implemento

    async def get_implementos(self, transportadora_id: UUID) -> List[Implemento]:
        """Retorna a lista de todos os implementos cadastrados da transportadora."""
        query = select(Implemento).where(Implemento.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_implemento_by_id(self, implemento_id: UUID, transportadora_id: UUID) -> Implemento:
        """Busca um implemento pelo ID. Levanta 404 se não encontrado."""
        query = select(Implemento).where(
            Implemento.id == implemento_id,
            Implemento.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        implemento = result.scalar_one_or_none()
        if not implemento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Implemento não encontrado."
            )
        return implemento

    async def update_implemento(self, implemento_id: UUID, data: ImplementoUpdate, transportadora_id: UUID) -> Implemento:
        """Atualiza dados cadastrais de um implemento."""
        implemento = await self.get_implemento_by_id( implemento_id, transportadora_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(implemento, key, value)

        self.session.add(implemento)
        await self.session.commit()
        await self.session.refresh(implemento)
        return implemento

    async def delete_implemento(self, implemento_id: UUID, transportadora_id: UUID) -> None:
        """Exclui um implemento do cadastro."""
        implemento = await self.get_implemento_by_id( implemento_id, transportadora_id)
        await self.session.delete(implemento)
        await self.session.commit()