from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MensagemCreate(BaseModel):
    motorista_id: UUID
    conteudo: str
    remetente: str # 'MOTORISTA' ou 'OPERADOR'

class MensagemResponse(BaseModel):
    id: UUID
    motorista_id: UUID
    conteudo: str
    remetente: str
    lido: bool
    created_at: datetime

    class Config:
        from_attributes = True
