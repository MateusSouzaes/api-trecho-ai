from fastapi import APIRouter, Depends, status
from typing import List, Optional
from uuid import UUID

from src.data_contexts.database_context import get_current_user
from src.models.usuario import Usuario
from src.dtos.whatsapp_dto import MensagemCreate, MensagemResponse
from src.services import WhatsappService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Central & RodovIA"])

@router.get("/mensagens", response_model=List[MensagemResponse])
async def get_mensagens(
    motorista_id: Optional[UUID] = None,
    current_user: Usuario = Depends(get_current_user),
    whatsapp_service: WhatsappService = Depends()
):
    """
    Retorna o histórico de conversas do WhatsApp.
    Opcionalmente filtra por um motorista específico.
    """
    messages = await whatsapp_service.get_mensagens(current_user.transportadora_id, motorista_id)
    return [MensagemResponse.model_validate(m) for m in messages]

@router.post("/mensagens", response_model=List[MensagemResponse], status_code=status.HTTP_201_CREATED)
async def send_mensagem(
    data: MensagemCreate,
    current_user: Usuario = Depends(get_current_user),
    whatsapp_service: WhatsappService = Depends()
):
    """
    Registra uma mensagem enviada.
    Caso a mensagem seja enviada pelo motorista ('MOTORISTA'), a assistente inteligente
    **RodovIA** ('SISTEMA_IA') responderá de forma automatizada simulando inteligência artificial.
    """
    messages = await whatsapp_service.send_mensagem(data, current_user.transportadora_id)
    return [MensagemResponse.model_validate(m) for m in messages]
