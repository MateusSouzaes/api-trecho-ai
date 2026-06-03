import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# 1. Mock database engine creation at import time to bypass asyncpg dialect import checks
import sqlalchemy.ext.asyncio
sqlalchemy.ext.asyncio.create_async_engine = MagicMock()
sqlalchemy.ext.asyncio.async_sessionmaker = MagicMock()

# 2. Pre-mock all services before importing src.main so routers import the mocks
import src.Services.AuthService as auth_service
auth_service.register_new_tenant = AsyncMock()
auth_service.authenticate_user = AsyncMock()

import src.Services.FrotaService as frota_service
frota_service.create_veiculo = AsyncMock()
frota_service.get_veiculos = AsyncMock()

import src.Services.PessoasService as pessoas_service
pessoas_service.create_motorista = AsyncMock()
pessoas_service.get_motorista_joined = AsyncMock()

import src.Services.ViagensService as viagens_service
viagens_service.create_viagem = AsyncMock()
viagens_service.launch_despesa = AsyncMock()

# Now import main and dependencies safely
from src.main import app
from src.DataContexts.DatabaseContext import get_current_user, get_current_tenant_session, get_session
from src.Models.Usuario import Usuario
from src.Models.Veiculo import Veiculo
from src.Dtos.MotoristaDto import MotoristaResponse
from src.Models.Viagem import Viagem
from src.Models.DespesaViagem import DespesaViagem
from src.Models.MensagemChat import MensagemChat

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

@pytest.fixture(autouse=True)
def override_dependencies():
    # Reset all service mocks before each test
    auth_service.register_new_tenant.reset_mock()
    auth_service.authenticate_user.reset_mock()
    frota_service.create_veiculo.reset_mock()
    frota_service.get_veiculos.reset_mock()
    pessoas_service.create_motorista.reset_mock()
    pessoas_service.get_motorista_joined.reset_mock()
    viagens_service.create_viagem.reset_mock()
    viagens_service.launch_despesa.reset_mock()
    
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
    yield
    app.dependency_overrides.clear()

# --- AUTH TESTS ---

def test_auth_register():
    auth_service.register_new_tenant.return_value = mock_user

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
    from src.Dtos.AuthDto import TokenResponse, UsuarioResponse
    auth_service.authenticate_user.return_value = TokenResponse(
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
    frota_service.create_veiculo.return_value = Veiculo(
        id=mock_veh_id,
        placa="ABC1D23",
        modelo="Constellation",
        marca="Volkswagen",
        ano_modelo=2022,
        capacidade_toneladas=Decimal("23.50"),
        status="ATIVA",
        consumo_medio_kml=Decimal("3.20")
    )

    payload = {
        "placa": "ABC1D23",
        "modelo": "Constellation",
        "marca": "Volkswagen",
        "ano_modelo": 2022,
        "capacidade_toneladas": 23.50,
        "status": "ATIVA",
        "consumo_medio_kml": 3.20,
        "codigo_fipe": "123456"
    }

    response = client.post("/frota/caminhoes", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["placa"] == "ABC1D23"
    assert response.json()["marca"] == "Volkswagen"

def test_get_veiculos():
    frota_service.get_veiculos.return_value = [
        Veiculo(
            id=uuid4(),
            placa="ABC1D23",
            modelo="Constellation",
            marca="Volkswagen",
            ano_modelo=2022,
            capacidade_toneladas=Decimal("23.5"),
            status="ATIVA",
            consumo_medio_kml=Decimal("3.2")
        )
    ]

    response = client.get("/frota/caminhoes", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["placa"] == "ABC1D23"

# --- DRIVER (MOTORISTAS) TESTS ---

def test_create_motorista():
    mock_mot_id = uuid4()
    pessoas_service.create_motorista.return_value = MotoristaResponse(
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
        status="ATIVA"
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
        "status": "ATIVA"
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
    
    viagens_service.create_viagem.return_value = Viagem(
        id=mock_trip_id,
        veiculo_id=mock_veh_id,
        motorista_id=mock_mot_id,
        origem_cidade="São Paulo",
        destino_cidade="Curitiba",
        km_inicial=Decimal("100.00"),
        valor_frete=Decimal("1500.00"),
        status="ATIVA",
        data_partida=datetime(2026, 6, 2, tzinfo=timezone.utc)
    )

    payload = {
        "veiculo_id": str(mock_veh_id),
        "motorista_id": str(mock_mot_id),
        "origem_cidade": "São Paulo",
        "destino_cidade": "Curitiba",
        "km_inicial": 100.00,
        "valor_frete": 1500.00,
        "status": "ATIVA",
        "data_partida": "2026-06-02T12:00:00Z"
    }

    response = client.post("/viagens", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["origem_cidade"] == "São Paulo"
    assert float(response.json()["valor_frete"]) == 1500.00

# --- EXPENSES (DESPESAS) TESTS ---

def test_launch_despesa():
    mock_trip_id = uuid4()
    mock_exp_id = uuid4()
    
    viagens_service.launch_despesa.return_value = DespesaViagem(
        id=mock_exp_id,
        viagem_id=mock_trip_id,
        tipo_despesa="COMBUSTIVEL",
        valor=Decimal("500.00"),
        descricao="Posto Graal"
    )

    payload = {
        "tipo_despesa": "COMBUSTIVEL",
        "valor": 500.00,
        "descricao": "Posto Graal"
    }

    response = client.post(f"/viagens/{mock_trip_id}/despesas", json=payload, headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 201
    assert response.json()["tipo_despesa"] == "COMBUSTIVEL"
    assert float(response.json()["valor"]) == 500.00

# --- DASHBOARD TESTS ---

def test_dashboard_lucratividade():
    mock_trip_id = uuid4()
    mock_veh_id = uuid4()
    mock_mot_id = uuid4()
    
    mock_viagem = Viagem(
        id=mock_trip_id,
        veiculo_id=mock_veh_id,
        motorista_id=mock_mot_id,
        origem_cidade="São Paulo",
        destino_cidade="Curitiba",
        km_inicial=Decimal("100.00"),
        valor_frete=Decimal("1500.00"),
        status="ATIVA",
        data_partida=datetime(2026, 6, 2, tzinfo=timezone.utc)
    )

    mock_despesa = DespesaViagem(
        id=uuid4(),
        viagem_id=mock_trip_id,
        tipo_despesa="COMBUSTIVEL",
        valor=Decimal("500.00"),
        descricao="Diesel"
    )

    # Mocking database query executions for get_lucratividade_dashboard
    # 1st execution resolves to voyages query result
    mock_res_viagens = MagicMock()
    mock_res_viagens.scalars.return_value.all.return_value = [mock_viagem]

    # 2nd execution resolves to despesas query result
    mock_res_despesas = MagicMock()
    mock_res_despesas.scalars.return_value.all.return_value = [mock_despesa]

    # Configure side effect for execute
    mock_session.execute.side_effect = [mock_res_viagens, mock_res_despesas]

    response = client.get("/dashboard/lucratividade", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response.status_code == 200
    assert float(response.json()["total_receita"]) == 1500.00
    assert float(response.json()["total_despesas"]) == 500.00
    assert float(response.json()["margem_contribuicao"]) == 1000.00
    assert len(response.json()["alertas"]) == 0

# --- WHATSAPP & RODOVIA AI TESTS ---

def test_whatsapp_rodovia_assistant():
    mock_mot_id = uuid4()
    
    pessoas_service.get_motorista_joined.return_value = True # Dummy return to pass check

    # Mock session execution return for WhatsApp get messages
    mock_msg_id = uuid4()
    mock_msg = MensagemChat(
        id=mock_msg_id,
        motorista_id=mock_mot_id,
        conteudo="Mensagem teste",
        remetente="OPERADOR",
        lido=True,
        created_at=datetime.now()
    )
    mock_res_msgs = MagicMock()
    mock_res_msgs.scalars.return_value.all.return_value = [mock_msg]
    mock_session.execute.return_value = mock_res_msgs

    # Test listing messages
    response_list = client.get(f"/whatsapp/mensagens?motorista_id={mock_mot_id}", headers={"Authorization": "Bearer fake-jwt-token"})
    assert response_list.status_code == 200
    assert len(response_list.json()) == 1

    # Test sending driver message and receiving RodovIA response
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
    assert "margem" in response.json()[1]["conteudo"] or "diesel" in response.json()[1]["conteudo"]
