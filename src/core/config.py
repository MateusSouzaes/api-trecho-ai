"""
Configurações centralizadas da aplicação.
Lê variáveis do .env e valida via Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação.
    
    Lê do .env com validação automática.
    Exemplo .env:
        DATABASE_URL=postgresql+asyncpg://user:password@localhost/trecho_ai
        SECRET_KEY=sua-chave-secreta-muito-forte
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    """

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trecho_ai"
    
    # Security
    secret_key: str = "dev-secret-change-in-production-very-strong-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    app_title: str = "Trecho.ai API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
