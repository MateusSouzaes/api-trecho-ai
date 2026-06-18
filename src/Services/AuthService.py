import logging
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status

from src.core.config import settings
from src.core.security import get_password_hash, verify_password, create_access_token
from src.Services.ApiClients import fetch_cep_info, fetch_cnpj_info
from src.Models.SharedModels import Endereco, Pessoa, PessoaJuridica, Transportadora
from src.Models.Usuario import Usuario
from src.Models.Sessao import Sessao
from src.Dtos.AuthDto import TransportadoraRegister, LoginRequest, TokenResponse, UsuarioResponse

logger = logging.getLogger(__name__)

async def register_new_tenant(data: TransportadoraRegister, session: AsyncSession) -> Usuario:
    """
    Executa o registro global da transportadora (Pessoa, PessoaJuridica, Endereco, Transportadora),
    e cria o usuário administrador.
    """
    # 1. Validar CNPJ e CEP via APIs reais (ou usar fallback)
    cnpj_info = await fetch_cnpj_info(data.cnpj)
    cep_info = await fetch_cep_info(data.cep)
    
    # Se CNPJ já cadastrado
    query_cnpj = select(PessoaJuridica).where(PessoaJuridica.cnpj == data.cnpj)
    res_cnpj = await session.execute(query_cnpj)
    if res_cnpj.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado.")

    # Se email de usuário admin já cadastrado
    query_user = select(Usuario).where(Usuario.email == data.admin_email)
    res_user = await session.execute(query_user)
    if res_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="E-mail de administrador já cadastrado.")

    # 2. Criar Endereço
    endereco = Endereco(
        cep=data.cep,
        logradouro=data.logradouro,
        numero=data.numero,
        complemento=data.complemento,
        bairro=data.bairro,
        cidade=data.cidade,
        estado=data.estado
    )
    session.add(endereco)
    await session.flush()

    # 3. Criar Pessoa Geral
    pessoa = Pessoa(
        tipo_pessoa="JURIDICA",
        nome_razao_social=data.nome_razao_social,
        telefone=data.telefone,
        email=data.admin_email,
        endereco_id=endereco.id
    )
    session.add(pessoa)
    await session.flush()

    # 4. Criar Pessoa Jurídica
    pessoa_juridica = PessoaJuridica(
        pessoa_id=pessoa.id,
        cnpj=data.cnpj,
        nome_fantasia=data.nome_fantasia or data.nome_razao_social,
        inscricao_estadual=data.inscricao_estadual
    )
    session.add(pessoa_juridica)
    await session.flush()

    # 5. Criar Transportadora
    transportadora = Transportadora(
        pessoa_juridica_id=pessoa_juridica.pessoa_id,
        rntrc=data.rntrc,
        status_conta="ATIVA"
    )
    session.add(transportadora)
    await session.flush()

    # 6. Criar Usuário Admin
    hashed_pwd = get_password_hash(data.admin_password)
    usuario = Usuario(
        email=data.admin_email,
        hashed_password=hashed_pwd,
        nome=data.admin_nome,
        role="ADMIN",
        is_active=True,
        transportadora_id=transportadora.id
    )
    session.add(usuario)
    await session.flush()

    await session.commit()
    await session.refresh(usuario)
    return usuario

async def authenticate_user(data: LoginRequest, session: AsyncSession) -> TokenResponse:
    """
    Valida as credenciais do usuário, cria uma sessão e retorna o token de acesso.
    """
    query = select(Usuario).where(Usuario.email == data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conta inativa."
        )

    # Gerar JWT token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "transportadora_id": str(user.transportadora_id)}
    )

    # Registrar Sessão no banco
    sessao = Sessao(
        usuario_id=user.id,
        token=access_token,
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)).replace(tzinfo=None)
    )
    session.add(sessao)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        usuario=UsuarioResponse.model_validate(user)
    )
