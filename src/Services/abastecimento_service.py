from src.data_contexts.database_context import get_current_tenant_session
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status

from src.models.abastecimento import Abastecimento
from src.models.cavalo import Cavalo
from src.models.fornecedor import Fornecedor
from src.dtos.abastecimento_dto import AbastecimentoCreate

class AbastecimentoService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def create_abastecimento(self, data: AbastecimentoCreate, transportadora_id: UUID) -> Abastecimento:
        # Validate Cavalo
        query_cavalo = select(Cavalo).where(
            Cavalo.id == data.cavalo_id,
            Cavalo.transportadora_id == transportadora_id
        )
        res_cavalo = await self.session.execute(query_cavalo)
        if not res_cavalo.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Veículo (Cavalo) não encontrado."
            )

        # Validate Fornecedor
        query_forn = select(Fornecedor).where(
            Fornecedor.id == data.fornecedor_id,
            Fornecedor.transportadora_id == transportadora_id
        )
        res_forn = await self.session.execute(query_forn)
        if not res_forn.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fornecedor não encontrado."
            )

        abast = Abastecimento(
            transportadora_id=transportadora_id,
            cavalo_id=data.cavalo_id,
            fornecedor_id=data.fornecedor_id,
            viagem_id=data.viagem_id,
            data_abastecimento=data.data_abastecimento,
            hodometro_veiculo=data.hodometro_veiculo,
            tipo_combustivel=data.tipo_combustivel,
            quantidade_litros=data.quantidade_litros,
            valor_unitario_litro=data.valor_unitario_litro
        )
        self.session.add(abast)
        await self.session.commit()
        await self.session.refresh(abast)
        return abast

    async def get_abastecimentos(self, transportadora_id: UUID) -> List[Abastecimento]:
        query = select(Abastecimento).where(Abastecimento.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
