import pytest
import time
import jwt
from auth.auth_backend import gerar_token, verificar_token

SECRET_KEY = "chave_super_secreta"

def test_gerar_token_valido():
    token = gerar_token(usuario_id=1)
    assert isinstance(token, str)
    assert token.count('.') == 2  # JWT tem 3 partes separadas por ponto

def test_verificar_token_valido():
    token = gerar_token(usuario_id=42)
    payload = verificar_token(token)
    assert payload is not None
    assert payload['usuario_id'] == 42

def test_verificar_token_invalido():
    token_falso = "token.falso.quebrado"
    resultado = verificar_token(token_falso)
    assert resultado is None

def test_verificar_token_expirado():
    token_expirado = jwt.encode(
        {"usuario_id": 99, "exp": time.time() - 5},  # Expirado há 5s
        SECRET_KEY,
        algorithm="HS256"
    )
    resultado = verificar_token(token_expirado)
    assert resultado is None
