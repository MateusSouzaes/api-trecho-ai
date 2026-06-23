from src.data_contexts.database_context import get_current_tenant_session
from fastapi import Depends
from decimal import Decimal
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.viagem import Viagem
from src.models.despesa_viagem import DespesaViagem
from src.models.receita_viagem import ReceitaViagem
from src.dtos.dashboard_dto import DashboardResponse, AlertaDashboard



class DashboardService:
    def __init__(self, session: AsyncSession = Depends(get_current_tenant_session)):
        self.session = session

    async def get_lucratividade_dashboard(self, transportadora_id: UUID) -> DashboardResponse:
        """
        Retorna consolidados financeiros de FinOps (Receitas, Despesas, Margens)
        e gera alertas operacionais de viagens de baixo rendimento ou prejuízo.
        """
        # 1. Buscar viagens
        query_viagens = select(Viagem).where(Viagem.transportadora_id == transportadora_id)
        res_viagens = await self.session.execute(query_viagens)
        viagens = list(res_viagens.scalars().all())
        total_viagens = len(viagens)

        # 2. Buscar e somar receitas (faturamento/frete)
        query_receitas = select(ReceitaViagem).where(ReceitaViagem.transportadora_id == transportadora_id)
        res_receitas = await self.session.execute(query_receitas)
        receitas = list(res_receitas.scalars().all())
        total_receita = sum(r.valor for r in receitas) if receitas else Decimal("0.00")

        # 3. Buscar e somar despesas
        query_despesas = select(DespesaViagem).where(DespesaViagem.transportadora_id == transportadora_id)
        res_despesas = await self.session.execute(query_despesas)
        despesas = list(res_despesas.scalars().all())
        total_despesas = sum(d.valor for d in despesas) if despesas else Decimal("0.00")

        # 4. Margem de Contribuição
        margem_contribuicao = total_receita - total_despesas

        # Calcular percentual de lucro
        percentual_lucro = Decimal("0.00")
        if total_receita > 0:
            percentual_lucro = (margem_contribuicao / total_receita) * 100

        # 5. Processamento de alertas analíticos por viagem
        alertas = []
        for v in viagens:
            # Filtrar receitas e despesas desta viagem
            receitas_viagem = [r for r in receitas if r.viagem_id == v.id]
            despesas_viagem = [d for d in despesas if d.viagem_id == v.id]

            faturamento_viagem = sum(r.valor for r in receitas_viagem)
            custo_total_viagem = sum(d.valor for d in despesas_viagem)

            lucro_viagem = faturamento_viagem - custo_total_viagem

            # Alerta Crítico: Prejuízo
            if lucro_viagem < 0:
                alertas.append(
                    AlertaDashboard(
                        viagem_id=str(v.id),
                        mensagem=f"Viagem #{v.codigo_viagem} gerou PREJUÍZO de R$ {abs(lucro_viagem):.2f}.",
                        tipo="CORROSIVO_ALERTA"
                    )
                )
            # Alerta de Atenção: Margem muito baixa (< 15% do faturamento)
            elif faturamento_viagem > 0 and (lucro_viagem / faturamento_viagem) < 0.15:
                alertas.append(
                    AlertaDashboard(
                        viagem_id=str(v.id),
                        mensagem=f"Viagem #{v.codigo_viagem} operando com margem crítica abaixo de 15%.",
                        tipo="ATENCAO"
                    )
                )

        return DashboardResponse(
            total_receita=total_receita,
            total_despesas=total_despesas,
            margem_contribuicao=margem_contribuicao,
            total_viagens=total_viagens,
            percentual_lucro=percentual_lucro,
            alertas=alertas
        )