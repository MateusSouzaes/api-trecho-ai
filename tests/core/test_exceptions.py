import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from src.exceptions.exception_handlers import setup_exception_handlers, BusinessException

# Criar app FastAPI de teste
app = FastAPI()
setup_exception_handlers(app)

@app.get("/trigger-business-error")
def trigger_business_error():
    raise BusinessException(detail="Regra de negócio violada", error_code="BUSINESS_RULE_VIOLATION", status_code=422)

@app.get("/trigger-http-error")
def trigger_http_error():
    raise HTTPException(status_code=404, detail="Recurso não encontrado")

@app.get("/trigger-integrity-error")
def trigger_integrity_error():
    # Simula erro de integridade de banco de dados
    raise IntegrityError("select ...", params={}, orig=Exception("duplicate key value violates unique constraint"))

@app.get("/trigger-generic-error")
def trigger_generic_error():
    raise Exception("Erro interno inesperado")

client = TestClient(app, raise_server_exceptions=False)

def test_business_exception_handler():
    response = client.get("/trigger-business-error")
    assert response.status_code == 422
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["message"] == "Regra de negócio violada"
    assert json_data["error"]["code"] == "BUSINESS_RULE_VIOLATION"

def test_http_exception_handler():
    response = client.get("/trigger-http-error")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["error"]["message"] == "Recurso não encontrado"
    assert json_data["error"]["code"] == "NOT_FOUND"

def test_integrity_exception_handler():
    response = client.get("/trigger-integrity-error")
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["success"] is False
    assert "integridade" in json_data["error"]["message"].lower() or "duplicado" in json_data["error"]["message"].lower()
    assert json_data["error"]["code"] == "INTEGRITY_ERROR"

def test_generic_exception_handler():
    response = client.get("/trigger-generic-error")
    assert response.status_code == 500
    json_data = response.json()
    assert json_data["success"] is False
    assert "erro interno" in json_data["error"]["message"].lower()
    assert json_data["error"]["code"] == "INTERNAL_SERVER_ERROR"
