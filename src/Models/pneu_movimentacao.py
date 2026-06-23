import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from src.models.base_models import UUIDMixin

class PneuMovimentacao(UUIDMixin, table=True):
    __tablename__ = "pneu_movimentacao"
    __table_args__ = {"schema": "public"}

    pneu_id: uuid.UUID = Field(nullable=False, foreign_key="public.pneu.id")
    cavalo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.cavalo.id")
    implemento_id: Optional[uuid.UUID] = Field(default=None, foreign_key="public.implemento.id")
    
    data_instalacao: datetime = Field(nullable=False)
    hodometro_instalacao: int = Field(nullable=False)
    
    data_remocao: Optional[datetime] = Field(default=None)
    hodometro_remocao: Optional[int] = Field(default=None)
    motivo_remocao: Optional[str] = Field(default=None, max_length=100)
