import uuid
from sqlmodel import Field, SQLModel

class ViagemImplemento(SQLModel, table=True):
    __tablename__ = "viagem_implemento"
    __table_args__ = {"schema": "public"}

    viagem_id: uuid.UUID = Field(primary_key=True, foreign_key="public.viagem.id")
    implemento_id: uuid.UUID = Field(primary_key=True, foreign_key="public.implemento.id")
    ordem_engate: int = Field(nullable=False)
