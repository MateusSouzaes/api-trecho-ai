import pytest
from pydantic import ValidationError
from uuid import uuid4
from src.models.shared_models import Endereco, Pessoa, PessoaFisica, PessoaJuridica, Transportadora
from src.models.usuario import Usuario
from src.models.sessao import Sessao

def test_endereco_validation():
    # Valid Endereco
    end = Endereco(
        cep="12345-678",
        logradouro="Rua Teste",
        numero="123",
        bairro="Bairro Teste",
        cidade="Cidade Teste",
        estado="SP"
    )
    assert end.cep == "12345-678"
    assert end.estado == "SP"

    # Invalid Endereco (missing required fields)
    with pytest.raises(ValidationError):
        Endereco.model_validate({"cep": "12345-678"})

def test_pessoa_validation():
    pessoa = Pessoa(
        tipo_pessoa="FISICA",
        nome_razao_social="Mateus Souza",
        email="mateus@example.com"
    )
    assert pessoa.tipo_pessoa == "FISICA"
    assert pessoa.email == "mateus@example.com"

def test_pessoa_fisica_validation():
    pf = PessoaFisica(
        pessoa_id=uuid4(),
        cpf="123.456.789-00",
        rg="12.345.678-9"
    )
    assert pf.cpf == "123.456.789-00"

def test_pessoa_juridica_validation():
    pj = PessoaJuridica(
        pessoa_id=uuid4(),
        cnpj="12.345.678/0001-99"
    )
    assert pj.cnpj == "12.345.678/0001-99"

def test_transportadora_validation():
    trans = Transportadora(
        pessoa_juridica_id=uuid4(),
        rntrc="12345678"
    )
    assert trans.rntrc == "12345678"
    assert trans.status_conta == "ATIVA"

def test_usuario_validation():
    user = Usuario(
        email="admin@trecho.ai",
        hashed_password="hashedpassword123",
        nome="Administrador",
        transportadora_id=uuid4()
    )
    assert user.email == "admin@trecho.ai"
    assert user.is_active is True

    # Invalid email
    with pytest.raises(ValidationError):
        Usuario.model_validate({
            "email": "invalid-email",
            "hashed_password": "hashedpassword123",
            "transportadora_id": uuid4()
        })
