from src.data_contexts.database_context import get_current_tenant_session
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status

from src.models.ordem_servico import OrdemServico
from src.models.cavalo import Cavalo
from src.models.implemento import Implemento
from src.models.fornecedor import Fornecedor
from src.dtos.ordem_servico_dto import OrdemServicoCreate

class OrdemServicoService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def create_ordem_servico(self, data: OrdemServicoCreate, transportadora_id: UUID) -> OrdemServico:
        # Validate Cavalo
        if data.cavalo_id:
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

        # Validate Implemento
        if data.implemento_id:
            query_imp = select(Implemento).where(
                Implemento.id == data.implemento_id,
                Implemento.transportadora_id == transportadora_id
            )
            res_imp = await self.session.execute(query_imp)
            if not res_imp.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Implemento não encontrado."
                )

        # Validate Fornecedor
        if data.fornecedor_id:
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

        os_rec = OrdemServico(
            transportadora_id=transportadora_id,
            fornecedor_id=data.fornecedor_id,
            cavalo_id=data.cavalo_id,
            implemento_id=data.implemento_id,
            tipo_manutencao=data.tipo_manutencao,
            hodometro_veiculo=data.hodometro_veiculo,
            valor_total_pecas=data.valor_total_pecas,
            valor_total_mao_obra=data.valor_total_mao_obra,
            data_abertura=data.data_abertura
        )
        self.session.add(os_rec)
        await self.session.commit()
        await self.session.refresh(os_rec)
        return os_rec

    async def get_ordens_servico(self, transportadora_id: UUID) -> List[OrdemServico]:
        query = select(OrdemServico).where(OrdemServico.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
