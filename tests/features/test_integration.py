import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# 1. Mock database engine creation at import time to bypass asyncpg dialect import checks
import sqlalchemy.ext.asyncio
sqlalchemy.ext.asyncio.create_async_engine = MagicMock()
sqlalchemy.ext.asyncio.async_sessionmaker = MagicMock()

# Now import main and dependencies safely
from src.main import app
from src.data_contexts.database_context import get_current_user, get_current_tenant_session, get_session
from src.models.usuario import Usuario
from src.models.cavalo import Cavalo
from src.dtos.motorista_dto import MotoristaResponse
from src.models.viagem import Viagem
from src.models.despesa_viagem import DespesaViagem
from src.models.receita_viagem import ReceitaViagem
from src.models.mensagem_chat import MensagemChat

from src.services import (
    AuthService, FrotaService, PessoasService, ViagensService, DashboardService, WhatsappService
)

from fastapi.testclient import TestClient
from uuid import uuid4, UUID
from datetime import datetime, timezone
from decimal import Decimal

client = TestClient(app)

# Helper mock user
mock_user_id = uuid4()
mock_tenant_id = uuid4()
mock_user = Usuario(
    id=mock_user_id,
    email="admin@trecho.ai",
    hashed_password="hashedpassword",
    nome="Admin",
    role="ADMIN",
    is_active=True,
    transportadora_id=mock_tenant_id
)

# Mocked session
mock_session = AsyncMock()

# Mocked services
mock_auth_service = MagicMock(spec=AuthService)
mock_auth_service.register_new_tenant = AsyncMock()
mock_auth_service.authenticate_user = AsyncMock()

mock_frota_service = MagicMock(spec=FrotaService)
mock_frota_service.create_cavalo = AsyncMock()
mock_frota_service.get_cavalos = AsyncMock()

mock_pessoas_service = MagicMock(spec=PessoasService)
mock_pessoas_service.create_motorista = AsyncMock()
mock_pessoas_service.get_motorista_joined = AsyncMock()

mock_viagens_service = MagicMock(spec=ViagensService)
mock_viagens_service.create_viagem = AsyncMock()
mock_viagens_service.launch_despesa = AsyncMock()

mock_dashboard_service = MagicMock(spec=DashboardService)
mock_dashboard_service.get_lucratividade_dashboard = AsyncMock()

mock_whatsapp_service = MagicMock(spec=WhatsappService)
mock_whatsapp_service.get_mensagens = AsyncMock()
mock_whatsapp_service.send_mensagem = AsyncMock()

@pytest.fixture(autouse=True)
def override_dependencies():
    # Reset all service mocks before each test
    mock_auth_service.register_new_tenant.reset_mock()
    mock_auth_service.authenticate_user.reset_mock()
    mock_frota_service.create_cavalo.reset_mock()
    mock_frota_service.get_cavalos.reset_mock()
    mock_pessoas_service.create_motorista.reset_mock()
    mock_pessoas_service.get_motorista_joined.reset_mock()
    mock_viagens_service.create_viagem.reset_mock()
    mock_viagens_service.launch_despesa.reset_mock()
    mock_dashboard_service.get_lucratividade_dashboard.reset_mock()
    mock_whatsapp_service.get_mensagens.reset_mock()
    mock_whatsapp_service.send_mensagem.reset_mock()
    
    mock_session.execute.reset_mock()
    mock_session.commit.reset_mock()
    mock_session.rollback.reset_mock()
    mock_session.flush.reset_mock()
    mock_session.refresh.reset_mock()
    
    # Explicitly clear side effects and return values for session.execute
    mock_session.execute.side_effect = None
    mock_session.execute.return_value = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_current_tenant_session] = lambda: mock_session
    
    app.dependency_overrides[AuthService] = lambda: mock_auth_service
    app.dependency_overrides[FrotaService] = lambda: mock_frota_service
    app.dependency_overrides[PessoasService] = lambda: mock_pessoas_service
    app.dependency_overrides[ViagensService] = lambda: mock_viagens_service
    app.dependency_overrides[DashboardService] = lambda: mock_dashboard_service
    app.dependency_overrides[WhatsappService] = lambda: mock_whatsapp_service
    
    yield
    app.dependency_overrides.clear()

# --- AUTH TESTS ---

def test_auth_register():
    mock_auth_service.register_new_tenant.return_value = mock_user

    payload = {
        "cnpj": "12.345.678/0001-99",
        "nome_razao_social": "Trecho Logistica LTDA",
        "nome_fantasia": "Trecho Log",
        "inscricao_estadual": "123456",
        "telefone": "11999999999",
        "cep": "01001-000",
        "logradouro": "Praça da Sé",
        "numero": "123",
        "bairro": "Sé",
        "cidade": "São Paulo",
        "estado": "SP",
        "rntrc": "987654321",
        "admin_nome": "Admin",
        "admin_email": "admin@trecho.ai",
        "admin_password": "securepassword"
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "admin@trecho.ai"
    assert response.json()["role"] == "ADMIN"

def test_auth_login():
    from src.dtos.auth_dto import TokenResponse, UsuarioResponse
    mock_auth_service.authenticate_user.return_value = TokenResponse(
        access_token="fake-jwt-token",
        usuario=UsuarioResponse(
            id=mock_user_id,
            email="admin@trecho.ai",
            nome="Admin",
            role="ADMIN",
            transportadora_id=mock_tenant_id
        )
    )

    response = client.post("/auth/login", json={"email": "admin@trecho.ai", "password": "securepassword"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-jwt-token"
    assert response.json()["usuario"]["email"] == "admin@trecho.ai"

def test_auth_me_authenticated():
    response = client.get("/auth/me", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@trecho.ai"

# --- FLEET (FROTA) TESTS ---

def test_create_veiculo():
    mock_veh_id = uuid4()
    mock_frota_service.create_cavalo.return_value = Cavalo(
        id=mock_veh_id,
        transportadora_id=mock_tenant_id,
        placa="ABC1D23",
        renavam="1234567890",
        chassi="987654321",
        modelo="Constellation",
        marca="Volkswagen",
        quantidade_eixos=3,
        tipo_rodado="6x2",
        tara_kg=Decimal("8500.0"),
        hodometro_atual=1000,
        frota_propria=True,
        status_veiculo="DISPONIVEL"
    )

    payload = {
        "placa": "ABC1D23",
        "renavam": "1234567890",
        "chassi": "987654321",
        "modelo": "Constellation",
        "marca": "Volkswagen",
        "quantidade_eixos": 3,
        "tipo_rodado": "6x2",
        "tara_kg": 8500.0,
        "hodometro_atual": 1000,
        "frota_propria": True,
        "status_veiculo": "DISPONIVEL"
    }

    response = client.post("/frota/caminhoes", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["placa"] == "ABC1D23"
    assert response.json()["marca"] == "Volkswagen"

def test_get_veiculos():
    mock_frota_service.get_cavalos.return_value = [
        Cavalo(
            id=uuid4(),
            transportadora_id=mock_tenant_id,
            placa="ABC1D23",
            renavam="1234567890",
            chassi="987654321",
            modelo="Constellation",
            marca="Volkswagen",
            quantidade_eixos=3,
            tipo_rodado="6x2",
            tara_kg=Decimal("8500.0"),
            hodometro_atual=1000,
            frota_propria=True,
            status_veiculo="DISPONIVEL"
        )
    ]

    response = client.get("/frota/caminhoes", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["placa"] == "ABC1D23"

# --- DRIVER (MOTORISTAS) TESTS ---

def test_create_motorista():
    mock_mot_id = uuid4()
    mock_pessoas_service.create_motorista.return_value = MotoristaResponse(
        id=mock_mot_id,
        nome="Mateus Driver",
        telefone="11988888888",
        email="driver@example.com",
        cpf="12345678909",
        rg="12.345.678-9",
        data_nascimento=datetime(1990, 5, 10, tzinfo=timezone.utc),
        cnh_numero="99999999",
        cnh_categoria="D",
        cnh_validade=datetime(2030, 5, 10, tzinfo=timezone.utc),
        cnh_pontos=0,
        status_operacional="DISPONIVEL"
    )

    payload = {
        "nome": "Mateus Driver",
        "telefone": "11988888888",
        "email": "driver@example.com",
        "cpf": "123.456.789-09",
        "rg": "12.345.678-9",
        "data_nascimento": "1990-05-10T00:00:00Z",
        "cnh_numero": "99999999",
        "cnh_categoria": "D",
        "cnh_validade": "2030-05-10T00:00:00Z",
        "status_operacional": "DISPONIVEL"
    }

    response = client.post("/pessoas/motoristas", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["nome"] == "Mateus Driver"
    assert response.json()["cnh_categoria"] == "D"

# --- TRIP (VIAGENS) TESTS ---

def test_create_viagem():
    mock_trip_id = uuid4()
    mock_veh_id = uuid4()
    mock_mot_id = uuid4()
    mock_addr_orig = uuid4()
    mock_addr_dest = uuid4()
    
    mock_viagens_service.create_viagem.return_value = Viagem(
        id=mock_trip_id,
        transportadora_id=mock_tenant_id,
        cavalo_id=mock_veh_id,
        motorista_id=mock_mot_id,
        endereco_origem_id=mock_addr_orig,
        endereco_destino_id=mock_addr_dest,
        hodometro_inicial=1000,
        status_operacional="PLANEJADA",
        status_financeiro="PENDENTE",
        data_inicio=datetime(2026, 6, 2, tzinfo=timezone.utc)
    )

    payload = {
        "cavalo_id": str(mock_veh_id),
        "motorista_id": str(mock_mot_id),
        "endereco_origem_id": str(mock_addr_orig),
        "endereco_destino_id": str(mock_addr_dest),
        "hodometro_inicial": 1000,
        "status_operacional": "PLANEJADA",
        "status_financeiro": "PENDENTE",
        "data_inicio": "2026-06-02T12:00:00Z"
    }

    response = client.post("/viagens", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["endereco_origem_id"] == str(mock_addr_orig)
    assert response.json()["hodometro_inicial"] == 1000

# --- EXPENSES (DESPESAS) TESTS ---

def test_launch_despesa():
    mock_trip_id = uuid4()
    mock_exp_id = uuid4()
    
    mock_viagens_service.launch_despesa.return_value = DespesaViagem(
        id=mock_exp_id,
        transportadora_id=mock_tenant_id,
        viagem_id=mock_trip_id,
        categoria="COMBUSTIVEL",
        valor=Decimal("500.00"),
        data_despesa=datetime(2026, 6, 2, tzinfo=timezone.utc),
        url_comprovante="http://receipts.com/1"
    )

    payload = {
        "categoria": "COMBUSTIVEL",
        "valor": 500.00,
        "data_despesa": "2026-06-02T12:00:00Z",
        "url_comprovante": "http://receipts.com/1"
    }

    response = client.post(f"/viagens/{mock_trip_id}/despesas", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["categoria"] == "COMBUSTIVEL"
    assert float(response.json()["valor"]) == 500.00

# --- DASHBOARD TESTS ---

def test_dashboard_lucratividade():
    from src.dtos.dashboard_dto import DashboardResponse
    mock_dashboard_service.get_lucratividade_dashboard.return_value = DashboardResponse(
        total_receita=Decimal("1500.00"),
        total_despesas=Decimal("500.00"),
        margem_contribuicao=Decimal("1000.00"),
        total_viagens=1,
        percentual_lucro=Decimal("66.67"),
        alertas=[]
    )

    response = client.get("/dashboard/lucratividade", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 200
    assert float(response.json()["total_receita"]) == 1500.00
    assert float(response.json()["total_despesas"]) == 500.00
    assert float(response.json()["margem_contribuicao"]) == 1000.00
    assert len(response.json()["alertas"]) == 0

# --- WHATSAPP & RODOVIA AI TESTS ---

def test_whatsapp_rodovia_assistant():
    mock_mot_id = uuid4()
    
    # Mock listing messages
    mock_msg_id = uuid4()
    mock_msg = MensagemChat(
        id=mock_msg_id,
        transportadora_id=mock_tenant_id,
        motorista_id=mock_mot_id,
        conteudo="Mensagem teste",
        remetente="OPERADOR",
        lido=True,
        created_at=datetime.now()
    )
    mock_whatsapp_service.get_mensagens.return_value = [mock_msg]
    
    # Test listing messages
    response_list = client.get(f"/whatsapp/mensagens?motorista_id={mock_mot_id}", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response_list.status_code == 200
    assert len(response_list.json()) == 1

    # Test sending driver message and receiving RodovIA response
    mock_ai_msg = MensagemChat(
        id=uuid4(),
        transportadora_id=mock_tenant_id,
        motorista_id=mock_mot_id,
        conteudo="RodovIA: Analisando as últimas viagens da frota. A sua viagem atual está operando com uma margem de contribuição saudável.",
        remetente="SISTEMA_IA",
        lido=False,
        created_at=datetime.now()
    )
    mock_driver_msg = MensagemChat(
        id=uuid4(),
        transportadora_id=mock_tenant_id,
        motorista_id=mock_mot_id,
        conteudo="Como está o lucro da minha viagem?",
        remetente="MOTORISTA",
        lido=True,
        created_at=datetime.now()
    )
    mock_whatsapp_service.send_mensagem.return_value = [mock_driver_msg, mock_ai_msg]

    payload = {
        "motorista_id": str(mock_mot_id),
        "conteudo": "Como está o lucro da minha viagem?",
        "remetente": "MOTORISTA"
    }

    response = client.post("/whatsapp/mensagens", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert len(response.json()) == 2
    
    # First message: Driver message
    assert response.json()[0]["remetente"] == "MOTORISTA"
    # Second message: RodovIA AI response
    assert response.json()[1]["remetente"] == "SISTEMA_IA"
    assert "RodovIA" in response.json()[1]["conteudo"]
