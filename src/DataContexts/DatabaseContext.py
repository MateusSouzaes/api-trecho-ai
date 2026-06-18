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

async def seed_operational_data(session: AsyncSession, transportadora_id: UUID, admin_pessoa_id: UUID) -> None:
    """Semeia dados operacionais de demonstração (caminhões, motoristas, viagens, custos, whatsapp)."""
    from datetime import datetime, timedelta
    from decimal import Decimal
    from src.Models import Endereco, Pessoa, PessoaFisica, MotoristaPerfil, Cavalo, Implemento, Viagem, DespesaViagem, ReceitaViagem, MensagemChat
    
    logger.info("🌱 Semeando dados operacionais de teste...")
    try:
        # 1. Endereços adicionais para Rotas
        end_origem = Endereco(
            cep="11015-002",
            logradouro="Avenida Portuária",
            numero="100",
            bairro="Porto",
            cidade="Santos",
            estado="SP"
        )
        end_destino = Endereco(
            cep="78740-022",
            logradouro="Rodovia BR-163",
            numero="KM 12",
            bairro="Distrito Industrial",
            cidade="Rondonópolis",
            estado="MT"
        )
        session.add(end_origem)
        session.add(end_destino)
        await session.flush()
        
        # 2. Motoristas (Pessoas Físicas)
        p_joao = Pessoa(
            tipo_pessoa="FISICA",
            nome_razao_social="João da Silva",
            telefone="(13) 99888-1122",
            email="joao.silva@express.com",
            endereco_id=end_origem.id
        )
        session.add(p_joao)
        await session.flush()
        
        pf_joao = PessoaFisica(
            pessoa_id=p_joao.id,
            cpf="11122233344",
            rg="223334445",
            data_nascimento=datetime(1985, 5, 12)
        )
        session.add(pf_joao)
        await session.flush()
        
        motorista_joao = MotoristaPerfil(
            transportadora_id=transportadora_id,
            pessoa_fisica_id=p_joao.id,
            cnh_numero="12345678900",
            cnh_categoria="E",
            cnh_validade=datetime(2029, 10, 15),
            cnh_pontos=0,
            status_operacional="EM_VIAGEM"
        )
        session.add(motorista_joao)
        
        p_carlos = Pessoa(
            tipo_pessoa="FISICA",
            nome_razao_social="Carlos Souza",
            telefone="(66) 99777-3344",
            email="carlos.souza@express.com",
            endereco_id=end_destino.id
        )
        session.add(p_carlos)
        await session.flush()
        
        pf_carlos = PessoaFisica(
            pessoa_id=p_carlos.id,
            cpf="22233344455",
            rg="334445556",
            data_nascimento=datetime(1990, 8, 22)
        )
        session.add(pf_carlos)
        await session.flush()
        
        motorista_carlos = MotoristaPerfil(
            transportadora_id=transportadora_id,
            pessoa_fisica_id=p_carlos.id,
            cnh_numero="98765432100",
            cnh_categoria="D",
            cnh_validade=datetime(2028, 4, 20),
            cnh_pontos=5,
            status_operacional="DISPONIVEL"
        )
        session.add(motorista_carlos)
        await session.flush()

        # 3. Cavalos Mecânicos (Caminhões)
        cavalo_volvo = Cavalo(
            transportadora_id=transportadora_id,
            placa="ABC1D23",
            renavam="12345678901",
            chassi="9BWZZZ377VT123456",
            marca="Volvo",
            modelo="Volvo FH 540 Globetrotter",
            quantidade_eixos=3,
            tipo_rodado="6X4",
            tara_kg=Decimal("8900.0"),
            hodometro_atual=125000,
            frota_propria=True,
            status_veiculo="DISPONIVEL"
        )
        cavalo_scania = Cavalo(
            transportadora_id=transportadora_id,
            placa="XYZ9W87",
            renavam="98765432109",
            chassi="9BWZZZ377VT987654",
            marca="Scania",
            modelo="Scania R450",
            quantidade_eixos=3,
            tipo_rodado="6X2",
            tara_kg=Decimal("8700.0"),
            hodometro_atual=240300,
            frota_propria=True,
            status_veiculo="DISPONIVEL"
        )
        session.add(cavalo_volvo)
        session.add(cavalo_scania)
        await session.flush()

        # 4. Implementos (Reboques)
        impl_graneleiro = Implemento(
            transportadora_id=transportadora_id,
            placa="MNO2E34",
            renavam="55566677788",
            chassi="9BWZZZ999VT111222",
            tipo_implemento="SEMIRREBOQUE",
            tipo_carroceria="GRANELEIRO",
            quantidade_eixos=3,
            tara_kg=Decimal("8500.0"),
            capacidade_carga_kg=Decimal("32000.0"),
            status_veiculo="DISPONIVEL"
        )
        session.add(impl_graneleiro)
        await session.flush()

        # 5. Viagens
        viagem_rota = Viagem(
            transportadora_id=transportadora_id,
            motorista_id=motorista_joao.id,
            cavalo_id=cavalo_volvo.id,
            endereco_origem_id=end_origem.id,
            endereco_destino_id=end_destino.id,
            data_inicio=datetime.now() - timedelta(hours=6),
            hodometro_inicial=124000,
            status_operacional="EM_ROTA",
            status_financeiro="PENDENTE"
        )
        viagem_concluida = Viagem(
            transportadora_id=transportadora_id,
            motorista_id=motorista_carlos.id,
            cavalo_id=cavalo_scania.id,
            endereco_origem_id=end_origem.id,
            endereco_destino_id=end_destino.id,
            data_inicio=datetime.now() - timedelta(days=5),
            data_fim=datetime.now() - timedelta(days=3),
            hodometro_inicial=238000,
            hodometro_final=240000,
            status_operacional="ENTREGUE",
            status_financeiro="PENDENTE"
        )
        session.add(viagem_rota)
        session.add(viagem_concluida)
        await session.flush()

        # 6. Despesas e Receitas da Viagem Concluída
        d1 = DespesaViagem(
            transportadora_id=transportadora_id,
            viagem_id=viagem_concluida.id,
            categoria="COMBUSTIVEL",
            valor=Decimal("3500.00"),
            data_despesa=datetime.now() - timedelta(days=4)
        )
        d2 = DespesaViagem(
            transportadora_id=transportadora_id,
            viagem_id=viagem_concluida.id,
            categoria="PEDAGIO",
            valor=Decimal("450.00"),
            data_despesa=datetime.now() - timedelta(days=4)
        )
        session.add(d1)
        session.add(d2)
        
        r1 = ReceitaViagem(
            transportadora_id=transportadora_id,
            viagem_id=viagem_concluida.id,
            cliente_pessoa_id=admin_pessoa_id, 
            tipo_receita="FRETE_VALOR",
            valor=Decimal("9800.00"),
            status_pagamento="A_RECEBER"
        )
        session.add(r1)
        
        # 7. Mensagem Chat
        msg1 = MensagemChat(
            transportadora_id=transportadora_id,
            motorista_id=motorista_joao.id,
            conteudo="Olá João, tudo pronto para iniciar a rota Santos-Rondonópolis?",
            remetente="OPERADOR",
            lido=True,
            created_at=datetime.now() - timedelta(hours=2)
        )
        msg2 = MensagemChat(
            transportadora_id=transportadora_id,
            motorista_id=motorista_joao.id,
            conteudo="Tudo pronto sim, chefe! Já carreguei a soja e estou saindo do porto.",
            remetente="MOTORISTA",
            lido=True,
            created_at=datetime.now() - timedelta(hours=1.9)
        )
        msg3 = MensagemChat(
            transportadora_id=transportadora_id,
            motorista_id=motorista_joao.id,
            conteudo="Excelente viagem. Qualquer ocorrência na BR-163 nos avise.",
            remetente="OPERADOR",
            lido=True,
            created_at=datetime.now() - timedelta(hours=1.8)
        )
        session.add(msg1)
        session.add(msg2)
        session.add(msg3)
        
        await session.commit()
        logger.info("🌱 Seed operacional de teste concluído com sucesso!")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Falha ao semear dados operacionais: {str(e)}")

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
                logger.info("🌱 Seed admin concluído com sucesso (admin@trecho.ai / admin123)!")
                
                # Semeia dados operacionais
                await seed_operational_data(session, transportadora.id, pessoa.id)
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Falha ao semear banco de dados: {str(e)}")
        else:
            logger.info("🌱 Usuário admin@trecho.ai já cadastrado. Verificando dados operacionais...")
            try:
                from src.Models.MotoristaPerfil import MotoristaPerfil
                from src.Models.SharedModels import Transportadora
                
                query_mot = select(MotoristaPerfil).where(MotoristaPerfil.transportadora_id == admin.transportadora_id)
                res_mot = await session.execute(query_mot)
                if not res_mot.scalars().first():
                    query_t = select(Transportadora).where(Transportadora.id == admin.transportadora_id)
                    res_t = await session.execute(query_t)
                    trans = res_t.scalar_one_or_none()
                    if trans:
                        await seed_operational_data(session, admin.transportadora_id, trans.pessoa_juridica_id)
            except Exception as ex:
                logger.error(f"❌ Falha ao verificar/semear dados operacionais incrementais: {str(ex)}")

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
