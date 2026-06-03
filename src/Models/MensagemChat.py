from datetime import datetime
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin
from uuid import UUID

class MensagemChat(UUIDMixin, table=True):
    __tablename__ = "mensagem_chat"
    __table_args__ = {"schema": "public"}

    transportadora_id: UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    motorista_id: UUID = Field(nullable=False, foreign_key="public.motorista_perfil.id")
    conteudo: str = Field(nullable=False)
    remetente: str = Field(max_length=20, nullable=False) # 'MOTORISTA', 'OPERADOR', 'SISTEMA_IA'
    lido: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
