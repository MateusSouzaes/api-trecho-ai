from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.Models.Viagem import Viagem
from src.Models.DespesaViagem import DespesaViagem
from src.Dtos.DashboardDto import DashboardResponse, AlertaDashboard

async def get_lucratividade_dashboard(session: AsyncSession) -> DashboardResponse:
    """
    Retorna consolidados financeiros de FinOps (Receitas, Despesas, Margens)
    e gera alertas operacionais de viagens de baixo rendimento ou prejuízo.
    """
    # 1. Total de viagens e Receita Bruta (fretes)
    query_viagens = select(Viagem)
    res_viagens = await session.execute(query_viagens)
    viagens = list(res_viagens.scalars().all())
    
    total_receita = sum(v.valor_frete for v in viagens) if viagens else Decimal("0.00")
    total_viagens = len(viagens)

    # 2. Total de Despesas
    query_despesas = select(DespesaViagem)
    res_despesas = await session.execute(query_despesas)
    despesas = list(res_despesas.scalars().all())
    total_despesas = sum(d.valor for d in despesas) if despesas else Decimal("0.00")

    # 3. Margem de Contribuição
    margem_contribuicao = total_receita - total_despesas
    
    # Calcular percentual de lucro
    percentual_lucro = Decimal("0.00")
    if total_receita > 0:
        percentual_lucro = (margem_contribuicao / total_receita) * 100

    # 4. Processamento de alertas analíticos por viagem
    alertas = []
    for v in viagens:
        # Filtrar despesas desta viagem específica
        despesas_viagem = [d for d in despesas if d.viagem_id == v.id]
        custo_total_viagem = sum(d.valor for d in despesas_viagem)
        lucro_viagem = v.valor_frete - custo_total_viagem
        
        # Alerta Crítico: Prejuízo
        if lucro_viagem < 0:
            alertas.append(
                AlertaDashboard(
                    viagem_id=str(v.id),
                    mensagem=f"Viagem de {v.origem_cidade} para {v.destino_cidade} gerou PREJUÍZO de R$ {abs(lucro_viagem):.2f}.",
                    tipo="CORROSIVO_ALERTA"
                )
            )
        # Alerta de Atenção: Margem muito baixa (< 15% do frete)
        elif v.valor_frete > 0 and (lucro_viagem / v.valor_frete) < 0.15:
            alertas.append(
                AlertaDashboard(
                    viagem_id=str(v.id),
                    mensagem=f"Viagem de {v.origem_cidade} para {v.destino_cidade} operando com margem crítica abaixo de 15%.",
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
