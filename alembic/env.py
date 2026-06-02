"""
Ambiente de Alembic para migrações assíncronas com SQLModel.
Suporta isolamento multi-tenant via schemas dinâmicos.
"""

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, URL, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from alembic import context
from sqlmodel import SQLModel

# Importar settings e models
from src.core.config import settings

# Definir target_metadata a partir do SQLModel
target_metadata = SQLModel.metadata

# Configuração do Alembic
config = context.config

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_connection_url() -> str:
    """Obtém URL de conexão do .env"""
    return settings.database_url


def run_migrations_offline() -> None:
    """
    Executa migrações em modo 'offline' (sem conexão real com o banco).
    Útil para gerar scripts SQL que serão executados manualmente depois.
    """
    url = get_connection_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Executa migrações em modo 'online' (com conexão real).
    Recomendado para desenvolvimento e CI/CD.
    
    Para PostgreSQL assíncrono, cria um AsyncEngine e processa migrações
    em contexto assíncrono.
    """
    # Criar URL de conexão
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.database_url.split("://")[1].split(":")[0],
        password=settings.database_url.split(":")[1].split("@")[0],
        host=settings.database_url.split("@")[1].split(":")[0],
        port=int(settings.database_url.split(":")[2].split("/")[0]),
        database=settings.database_url.split("/")[-1],
    )
    
    # Criar async engine
    connectable = create_async_engine(
        url,
        echo=False,
        poolclass=pool.NullPool,
    )

    async def do_run_migrations(connection: AsyncConnection) -> None:
        """Executa as migrações de forma assíncrona"""
        await connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    import asyncio
    
    async def run_migrations() -> None:
        """Abre conexão assíncrona e executa migrações"""
        async with connectable.begin() as connection:
            await do_run_migrations(connection)

    asyncio.run(run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
