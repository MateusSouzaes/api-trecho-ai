"""Base models compartilhados entre features."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin para adicionar campos de auditoria de data"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UUIDMixin(SQLModel):
    """Mixin para adicionar campo UUID como primary key"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
