import logging
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from src.core.config import settings
from src.Models.Usuario import Usuario

logger = logging.getLogger(__name__)

# Engine assíncrono para PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Fornece conexão com o schema public (dados globais)."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_tenant_session(transportadora_id: UUID) -> AsyncGenerator[AsyncSession, None]:
    """Comuta dinamicamente o search_path para o schema do tenant."""
    async with async_session_maker() as session:
        try:
            schema_name = f"tenant_{str(transportadora_id).replace('-', '_')}"
            await session.execute(text(f"SET search_path TO {schema_name}"))
            yield session
        except Exception as e:
            logger.error(f"Erro ao comutar Tenant {transportadora_id}: {e}")
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Cria as extensões e tabelas base no startup da API."""
    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("✅ Banco de dados inicializado com sucesso")

async def close_db() -> None:
    """Fecha o pool de conexões com o banco."""
    await engine.dispose()
    logger.info("✅ Conexão com banco fechada")

# Configura o fluxo de token OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou expiradas",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> Usuario:
    """Decodifica o token JWT e recupera o Usuário autenticado."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
        
    query = select(Usuario).where(Usuario.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
        
    return user

async def get_current_tenant_session(
    current_user: Usuario = Depends(get_current_user)
) -> AsyncGenerator[AsyncSession, None]:
    """Dependência para obter conexão no contexto do tenant atual."""
    async for session in get_tenant_session(current_user.transportadora_id):
        yield session
