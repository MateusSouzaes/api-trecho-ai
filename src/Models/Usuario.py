import uuid
from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from src.Models.base_models import UUIDMixin, TimestampMixin

class Usuario(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "auth"}

    email: EmailStr = Field(nullable=False, unique=True, index=True)
    hashed_password: str = Field(nullable=False, max_length=255)
    nome: Optional[str] = Field(default=None, max_length=255)
    role: str = Field(default="USER", max_length=50)
    is_active: bool = Field(default=True)
    
    transportadora_id: uuid.UUID = Field(nullable=False, foreign_key="public.transportadora.id")
