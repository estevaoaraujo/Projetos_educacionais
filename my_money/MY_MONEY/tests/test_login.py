import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from run import app
from auth.auth_backend import registrar_usuario

@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.test_client() as cliente:
        yield cliente

def test_login_sucesso(cliente):
    # Corrigido: usar contexto de aplicação ao registrar usuário
    with app.app_context():
        registrar_usuario('usuario@teste.com', '123456')

    dados = {'email': 'usuario@teste.com', 'senha': '123456'}
    resposta = cliente.post('/login', json=dados)
    json_data = resposta.get_json()
    assert resposta.status_code == 200
    assert json_data is not None and 'token' in json_data

def test_login_erro(cliente):
    dados = {'email': 'emailinvalido@teste.com', 'senha': 'senhaerrada'}
    resposta = cliente.post('/login', json=dados)
    json_data = resposta.get_json()
    assert resposta.status_code == 401
    assert json_data is not None and 'erro' in json_data


