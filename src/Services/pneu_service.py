from src.data_contexts.database_context import get_current_tenant_session
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status
from datetime import datetime

from src.models.pneu import Pneu
from src.models.pneu_movimentacao import PneuMovimentacao
from src.models.cavalo import Cavalo
from src.models.implemento import Implemento
from src.dtos.pneu_dto import PneuCreate, PneuInstalarRequest, PneuRemoverRequest

class PneuService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def create_pneu(self, data: PneuCreate, transportadora_id: UUID) -> Pneu:
        pneu = Pneu(
            transportadora_id=transportadora_id,
            numero_fogo=data.numero_fogo,
            marca=data.marca,
            dimensao=data.dimensao,
            sulco_atual_mm=data.sulco_atual_mm,
            status_uso=data.status_uso or "ESTOQUE"
        )
        self.session.add(pneu)
        await self.session.commit()
        await self.session.refresh(pneu)
        return pneu

    async def get_pneus(self, transportadora_id: UUID) -> List[Pneu]:
        query = select(Pneu).where(Pneu.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def instalar_pneu(self, pneu_id: UUID, data: PneuInstalarRequest, transportadora_id: UUID) -> Pneu:
        # Get Pneu
        query_pneu = select(Pneu).where(Pneu.id == pneu_id, Pneu.transportadora_id == transportadora_id)
        res_pneu = await self.session.execute(query_pneu)
        pneu = res_pneu.scalar_one_or_none()
        if not pneu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pneu não encontrado.")

        if pneu.status_uso != "ESTOQUE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pneu não está em estoque.")

        # Update Pneu
        pneu.status_uso = "USO"
        pneu.cavalo_atual_id = data.cavalo_id
        pneu.implemento_atual_id = data.implemento_id
        pneu.eixo_atual = data.eixo
        pneu.posicao_atual = data.posicao
        self.session.add(pneu)

        # Log Movement
        mov = PneuMovimentacao(
            pneu_id=pneu.id,
            cavalo_id=data.cavalo_id,
            implemento_id=data.implemento_id,
            data_instalacao=data.data_instalacao,
            hodometro_instalacao=data.hodometro_instalacao
        )
        self.session.add(mov)
        await self.session.commit()
        await self.session.refresh(pneu)
        return pneu

    async def remover_pneu(self, pneu_id: UUID, data: PneuRemoverRequest, transportadora_id: UUID) -> Pneu:
        # Get Pneu
        query_pneu = select(Pneu).where(Pneu.id == pneu_id, Pneu.transportadora_id == transportadora_id)
        res_pneu = await self.session.execute(query_pneu)
        pneu = res_pneu.scalar_one_or_none()
        if not pneu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pneu não encontrado.")

        if pneu.status_uso != "USO":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pneu não está em uso.")

        # Find active installation record (where data_remocao is null)
        query_mov = select(PneuMovimentacao).where(
            PneuMovimentacao.pneu_id == pneu.id,
            PneuMovimentacao.data_remocao == None
        )
        res_mov = await self.session.execute(query_mov)
        mov = res_mov.scalar_one_or_none()
        if mov:
            mov.data_remocao = data.data_remocao
            mov.hodometro_remocao = data.hodometro_remocao
            mov.motivo_remocao = data.motivo_remocao
            self.session.add(mov)

            # Accumulate mileage
            mileage = data.hodometro_remocao - mov.hodometro_instalacao
            if mileage > 0:
                pneu.quilometragem_acumulada += mileage

        # Reset Pneu state
        pneu.status_uso = "ESTOQUE"
        pneu.sulco_atual_mm = data.novo_sulco_mm
        pneu.cavalo_atual_id = None
        pneu.implemento_atual_id = None
        pneu.eixo_atual = None
        pneu.posicao_atual = None
        self.session.add(pneu)

        await self.session.commit()
        await self.session.refresh(pneu)
        return pneu
