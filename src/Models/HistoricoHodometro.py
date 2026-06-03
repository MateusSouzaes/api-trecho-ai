import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin

class HistoricoHodometro(UUIDMixin, table=True):
    __tablename__ = "historico_hodometro"
    __table_args__ = {"schema": "public"}

    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
    cavalo_id: uuid.UUID = Field(nullable=False, foreign_key="public.cavalo.id")
    valor_leitura: int = Field(nullable=False)
    data_leitura: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    origem_leitura: str = Field(max_length=50, nullable=False)
    viagem_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.viagem.id")
