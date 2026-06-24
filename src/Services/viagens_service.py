from src.data_contexts.database_context import get_current_tenant_session
import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import Depends, HTTPException, status

from src.models.cavalo import Cavalo
from src.models.motorista_perfil import MotoristaPerfil
from src.models.viagem import Viagem
from src.models.despesa_viagem import DespesaViagem
from src.models.receita_viagem import ReceitaViagem
from src.dtos.viagem_dto import ViagemCreate, ViagemUpdate, DespesaCreate, ReceitaCreate

logger = logging.getLogger(__name__)



class ViagensService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def create_viagem(self, data: ViagemCreate, transportadora_id: UUID) -> Viagem:
        """
        Cria uma nova viagem após validar se o cavalo e o motorista existem
        e pertencem à transportadora.
        """
        # 1. Validar Cavalo
        query_cavalo = select(Cavalo).where(
            Cavalo.id == data.cavalo_id,
            Cavalo.transportadora_id == transportadora_id
        )
        res_cavalo = await self.session.execute(query_cavalo)
        if not res_cavalo.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cavalo mecânico não encontrado ou não pertence a esta transportadora."
            )

        # 2. Validar Motorista
        query_motorista = select(MotoristaPerfil).where(
            MotoristaPerfil.id == data.motorista_id,
            MotoristaPerfil.transportadora_id == transportadora_id
        )
        res_motorista = await self.session.execute(query_motorista)
        if not res_motorista.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Motorista não encontrado ou não pertence a esta transportadora."
            )

        # 3. Criar
        viagem = Viagem(
            transportadora_id=transportadora_id,
            motorista_id=data.motorista_id,
            cavalo_id=data.cavalo_id,
            endereco_origem_id=data.endereco_origem_id,
            endereco_destino_id=data.endereco_destino_id,
            data_inicio=data.data_inicio,
            hodometro_inicial=data.hodometro_inicial,
            status_operacional=data.status_operacional or "PLANEJADA",
            status_financeiro=data.status_financeiro or "PENDENTE"
        )
        self.session.add(viagem)
        await self.session.flush()

        # 4. Vincular implementos
        if data.implemento_ids:
            from src.models.implemento import Implemento
            from src.models.viagem_implemento import ViagemImplemento
            for idx, imp_id in enumerate(data.implemento_ids):
                query_imp = select(Implemento).where(
                    Implemento.id == imp_id,
                    Implemento.transportadora_id == transportadora_id
                )
                res_imp = await self.session.execute(query_imp)
                if not res_imp.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Implemento {imp_id} não encontrado."
                    )
                viagem_imp = ViagemImplemento(
                    viagem_id=viagem.id,
                    implemento_id=imp_id,
                    ordem_engate=idx + 1
                )
                self.session.add(viagem_imp)

        await self.session.commit()
        await self.session.refresh(viagem)
        return viagem

    async def get_viagens(self, transportadora_id: UUID) -> List[Viagem]:
        """Retorna todas as viagens cadastradas da transportadora."""
        query = select(Viagem).where(Viagem.transportadora_id == transportadora_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_viagem_by_id(self, viagem_id: UUID, transportadora_id: UUID) -> Viagem:
        """Retorna uma viagem pelo ID."""
        query = select(Viagem).where(
            Viagem.id == viagem_id,
            Viagem.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        viagem = result.scalar_one_or_none()
        if not viagem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Viagem não encontrada."
            )
        return viagem

    async def update_viagem(self, viagem_id: UUID, data: ViagemUpdate, transportadora_id: UUID) -> Viagem:
        """Atualiza dados de uma viagem."""
        viagem = await self.get_viagem_by_id( viagem_id, transportadora_id)

        update_data = data.model_dump(exclude_unset=True)

        # Validações extras para conclusão de viagem
        if "hodometro_final" in update_data and update_data["hodometro_final"] is not None:
            if update_data["hodometro_final"] < viagem.hodometro_inicial:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hodômetro final não pode ser menor que o hodômetro inicial."
                )

        for key, value in update_data.items():
            setattr(viagem, key, value)

        self.session.add(viagem)
        await self.session.commit()
        await self.session.refresh(viagem)
        return viagem

    async def delete_viagem(self, viagem_id: UUID, transportadora_id: UUID) -> None:
        """Exclui uma viagem do cadastro."""
        viagem = await self.get_viagem_by_id( viagem_id, transportadora_id)
        await self.session.delete(viagem)
        await self.session.commit()


    # --- DESPESAS SERVICES ---

    async def launch_despesa(self, viagem_id: UUID, data: DespesaCreate, transportadora_id: UUID) -> DespesaViagem:
        """Lança uma nova despesa vinculada a uma viagem existente."""
        # Verificar se viagem existe
        await self.get_viagem_by_id( viagem_id, transportadora_id)

        despesa = DespesaViagem(
            transportadora_id=transportadora_id,
            viagem_id=viagem_id,
            categoria=data.categoria.upper(),
            valor=data.valor,
            data_despesa=data.data_despesa,
            url_comprovante=data.url_comprovante
        )
        self.session.add(despesa)
        await self.session.commit()
        await self.session.refresh(despesa)
        return despesa

    async def get_despesas_by_viagem(self, viagem_id: UUID, transportadora_id: UUID) -> List[DespesaViagem]:
        """Retorna todas as despesas vinculadas a uma viagem específica."""
        await self.get_viagem_by_id( viagem_id, transportadora_id)
        query = select(DespesaViagem).where(
            DespesaViagem.viagem_id == viagem_id,
            DespesaViagem.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())


    # --- RECEITAS SERVICES ---

    async def launch_receita(self, viagem_id: UUID, data: ReceitaCreate, transportadora_id: UUID) -> ReceitaViagem:
        """Lança uma nova receita/frete vinculada a uma viagem."""
        # Verificar se viagem existe
        await self.get_viagem_by_id( viagem_id, transportadora_id)

        receita = ReceitaViagem(
            transportadora_id=transportadora_id,
            viagem_id=viagem_id,
            cliente_pessoa_id=data.cliente_pessoa_id,
            tipo_receita=data.tipo_receita.upper(),
            valor=data.valor,
            status_pagamento=data.status_pagamento or "A_RECEBER"
        )
        self.session.add(receita)
        await self.session.commit()
        await self.session.refresh(receita)
        return receita

    async def get_receitas_by_viagem(self, viagem_id: UUID, transportadora_id: UUID) -> List[ReceitaViagem]:
        """Retorna todas as receitas vinculadas a uma viagem."""
        await self.get_viagem_by_id( viagem_id, transportadora_id)
        query = select(ReceitaViagem).where(
            ReceitaViagem.viagem_id == viagem_id,
            ReceitaViagem.transportadora_id == transportadora_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())