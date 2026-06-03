import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.Models.MensagemChat import MensagemChat
from src.Dtos.WhatsappDto import MensagemCreate
from src.Services import PessoasService

logger = logging.getLogger(__name__)

async def get_mensagens(session: AsyncSession, transportadora_id: UUID, motorista_id: Optional[UUID] = None) -> List[MensagemChat]:
    """
    Retorna o histórico de conversas do WhatsApp da transportadora.
    Opcionalmente filtra por um motorista específico.
    """
    query = select(MensagemChat).where(MensagemChat.transportadora_id == transportadora_id)
    if motorista_id:
        query = query.where(MensagemChat.motorista_id == motorista_id)
    query = query.order_by(MensagemChat.created_at.asc())
    
    result = await session.execute(query)
    return list(result.scalars().all())

async def send_mensagem(session: AsyncSession, data: MensagemCreate, transportadora_id: UUID) -> List[MensagemChat]:
    """
    Registra uma mensagem enviada.
    Caso a mensagem seja enviada pelo motorista ('MOTORISTA'), a assistente inteligente
    **RodovIA** ('SISTEMA_IA') responderá de forma automatizada simulando inteligência artificial.
    """
    # 1. Validar se o motorista existe
    await PessoasService.get_motorista_joined(session, data.motorista_id, transportadora_id)

    # 2. Salvar mensagem principal
    msg = MensagemChat(
        transportadora_id=transportadora_id,
        motorista_id=data.motorista_id,
        conteudo=data.conteudo,
        remetente=data.remetente.upper(),
        lido=True
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    
    returned_messages = [msg]

    # 3. Se for do motorista, simular resposta da assistente virtual RodovIA
    if data.remetente.upper() == "MOTORISTA":
        text_lower = data.conteudo.lower()
        
        # Heurística de resposta inteligente da RodovIA
        if "lucro" in text_lower or "margem" in text_lower or "dinheiro" in text_lower:
            reply_text = "RodovIA: Analisando as últimas viagens da frota. A sua viagem atual está operando com uma margem de contribuição saudável. Mantenha a velocidade padrão para otimizar o consumo de diesel."
        elif "bloqueio" in text_lower or "cerca" in text_lower or "alerta" in text_lower:
            reply_text = "RodovIA: Atenção! Verifiquei sua rota e não há alertas de bloqueio ativo. Prossiga com cuidado na BR-101."
        elif "ajuda" in text_lower or "suporte" in text_lower or "socorro" in text_lower:
            reply_text = "RodovIA: Entendido. Estou notificando o operador de plantão na Central de Gestão Trecho.IA para entrar em contato imediato."
        else:
            reply_text = f"RodovIA: Olá! Recebi sua mensagem: '{data.conteudo}'. Suas coordenadas de GPS e logs de viagem estão sendo atualizados no dashboard em tempo real."

        ai_msg = MensagemChat(
            transportadora_id=transportadora_id,
            motorista_id=data.motorista_id,
            conteudo=reply_text,
            remetente="SISTEMA_IA",
            lido=False
        )
        session.add(ai_msg)
        await session.commit()
        await session.refresh(ai_msg)
        returned_messages.append(ai_msg)

    return returned_messages
