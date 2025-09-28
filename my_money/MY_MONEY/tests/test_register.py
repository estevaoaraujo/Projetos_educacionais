import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from run import app

@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.test_client() as cliente:
        yield cliente

def test_register_usuario_sucesso(cliente):
    dados = {'email': 'automato1@teste.com', 'senha': 'senha123'}
    resposta = cliente.post('/register', json=dados)
    assert resposta.status_code in [201, 400]  # 201 se novo, 400 se já existe
    if resposta.status_code == 201:
        assert resposta.get_json()['mensagem'] == 'Usuário registrado com sucesso'
    else:
        assert resposta.get_json()['erro'] == 'Usuário já existe'

def test_register_usuario_vazio(cliente):
    dados = {'email': '', 'senha': ''}
    resposta = cliente.post('/register', json=dados)
    assert resposta.status_code == 400
    assert 'erro' in resposta.get_json()

def test_register_email_invalido(cliente):
    dados = {'email': 'emailinvalido', 'senha': 'senha123'}
    resposta = cliente.post('/register', json=dados)
    assert resposta.status_code == 400
    assert resposta.get_json()['erro'] == 'Email inválido'
