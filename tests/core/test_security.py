import pytest
from datetime import timedelta
from jose import jwt
from src.core.security import get_password_hash, verify_password, create_access_token, verify_token
from src.core.config import settings

def test_password_hashing():
    password = "minhasenhasegura"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("outrasenha", hashed) is False

def test_jwt_token_generation_and_validation():
    data = {"sub": "user@example.com", "transportadora_id": "c35b8b62-9217-48f8-a003-88e5d0d4022a"}
    token = create_access_token(data, expires_delta=timedelta(minutes=15))
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user@example.com"
    assert decoded["transportadora_id"] == "c35b8b62-9217-48f8-a003-88e5d0d4022a"

def test_jwt_token_expired():
    # Test token expiration
    data = {"sub": "user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-10))
    
    decoded = verify_token(token)
    assert decoded is None
