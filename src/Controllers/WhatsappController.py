from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from src.DataContexts.DatabaseContext import get_current_tenant_session
from src.Dtos.WhatsappDto import MensagemCreate, MensagemResponse
from src.Services import WhatsappService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Central & RodovIA"])

@router.get("/mensagens", response_model=List[MensagemResponse])
async def get_mensagens(
    motorista_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Retorna o histórico de conversas do WhatsApp.
    Opcionalmente filtra por um motorista específico.
    """
    messages = await WhatsappService.get_mensagens(session, motorista_id)
    return [MensagemResponse.model_validate(m) for m in messages]

@router.post("/mensagens", response_model=List[MensagemResponse], status_code=status.HTTP_201_CREATED)
async def send_mensagem(
    data: MensagemCreate,
    session: AsyncSession = Depends(get_current_tenant_session)
):
    """
    Registra uma mensagem enviada.
    Caso a mensagem seja enviada pelo motorista ('MOTORISTA'), a assistente inteligente
    **RodovIA** ('SISTEMA_IA') responderá de forma automatizada simulando inteligência artificial.
    """
    messages = await WhatsappService.send_mensagem(session, data)
    return [MensagemResponse.model_validate(m) for m in messages]
