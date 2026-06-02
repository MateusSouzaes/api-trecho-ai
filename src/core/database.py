"""
Configuração de conexão com PostgreSQL usando SQLModel.
Suporta isolamento multi-tenant via schemas dinâmicos.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, event
from sqlmodel import SQLModel, select
from typing import AsyncGenerator, Optional
from uuid import UUID
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Engine assíncrono para PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Mude para True para debug de SQL
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
    """
    Dependência de sessão genérica do FastAPI.
    Fornece conexão com schema 'public' (dados globais).
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_tenant_session(
    transportadora_id: UUID,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência de sessão com isolamento multi-tenant.
    
    Comuta dinamicamente para o schema tenant_<id> do PostgreSQL.
    Garante que queries subsequentes acessem apenas dados do tenant.
    
    Args:
        transportadora_id: UUID da transportadora (tenant).
        
    Yields:
        AsyncSession contextualizada ao schema do tenant.
    """
    async with async_session_maker() as session:
        try:
            # Comuta para o schema do tenant
            schema_name = f"tenant_{transportadora_id}"
            await session.execute(text(f"SET search_path TO {schema_name}"))
            yield session
        except Exception as e:
            logger.error(f"Erro ao comutar Tenant {transportadora_id}: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.
    Deve ser chamado uma única vez na startup.
    """
    async with engine.begin() as conn:
        # Cria as extensões necessárias
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        
        # Cria as tabelas baseadas em SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("✅ Banco de dados inicializado com sucesso")


async def close_db() -> None:
    """
    Fecha a conexão com o banco.
    Deve ser chamado no shutdown da aplicação.
    """
    await engine.dispose()
    logger.info("✅ Conexão com banco fechada")