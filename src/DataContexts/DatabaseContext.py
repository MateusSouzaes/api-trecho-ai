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
import src.Models  # Garante o registro de metadados de todas as tabelas

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
    """Retorna uma sessão padrão no modelo Single-Schema."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    """Cria as extensões e tabelas base no startup da API."""
    async with engine.begin() as conn:
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS auth;'))
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS public;'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("✅ Banco de dados inicializado com sucesso")

    # Semeia dados iniciais de administração se necessário
    async with async_session_maker() as session:
        query = select(Usuario).where(Usuario.email == "admin@trecho.ai")
        res = await session.execute(query)
        admin = res.scalar_one_or_none()
        
        if not admin:
            logger.info("🌱 Semeando dados iniciais (admin@trecho.ai)...")
            from src.core.security import get_password_hash
            from src.Models import Endereco, Pessoa, PessoaJuridica, Transportadora
            
            try:
                # 1. Endereço
                endereco = Endereco(
                    cep="01310-100",
                    logradouro="Avenida Paulista",
                    numero="1000",
                    bairro="Bela Vista",
                    cidade="São Paulo",
                    estado="SP"
                )
                session.add(endereco)
                await session.flush()
                
                # 2. Pessoa
                pessoa = Pessoa(
                    tipo_pessoa="JURIDICA",
                    nome_razao_social="Trecho Transportes Ltda",
                    email="admin@trecho.ai",
                    endereco_id=endereco.id
                )
                session.add(pessoa)
                await session.flush()
                
                # 3. Pessoa Jurídica
                pessoa_juridica = PessoaJuridica(
                    pessoa_id=pessoa.id,
                    cnpj="00000000000100",
                    nome_fantasia="Trecho Transportes",
                    inscricao_estadual="123456789"
                )
                session.add(pessoa_juridica)
                await session.flush()
                
                # 4. Transportadora
                transportadora = Transportadora(
                    pessoa_juridica_id=pessoa_juridica.pessoa_id,
                    rntrc="1234567890",
                    status_conta="ATIVA"
                )
                session.add(transportadora)
                await session.flush()
                
                # 5. Usuário Admin
                hashed_pwd = get_password_hash("admin123")
                usuario = Usuario(
                    email="admin@trecho.ai",
                    hashed_password=hashed_pwd,
                    nome="Admin Trecho",
                    role="ADMIN",
                    is_active=True,
                    transportadora_id=transportadora.id
                )
                session.add(usuario)
                await session.commit()
                logger.info("🌱 Seed concluído com sucesso (admin@trecho.ai / admin123)!")
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Falha ao semear banco de dados: {str(e)}")
        else:
            logger.info("🌱 Usuário admin@trecho.ai já cadastrado. Ignorando seed.")

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
