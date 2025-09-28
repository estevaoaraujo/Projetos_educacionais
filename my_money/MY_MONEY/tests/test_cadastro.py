import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from run import app

@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.test_client() as cliente:
        yield cliente

def test_cadastro_usuario_sucesso(cliente):
    dados = {'email': 'teste_automato@teste.com', 'senha': 'senha123'}
    resposta = cliente.post('/cadastro', json=dados)
    assert resposta.status_code in [201, 400]
    if resposta.status_code == 201:
        assert resposta.get_json()['mensagem'] == 'Usuário registrado com sucesso'
    else:
        assert resposta.get_json()['erro'] == 'Usuário já existe'

def test_cadastro_usuario_vazio(cliente):
    dados = {'email': '', 'senha': ''}
    resposta = cliente.post('/cadastro', json=dados)
    assert resposta.status_code == 400
    assert 'erro' in resposta.get_json()

def test_cadastro_email_invalido(cliente):
    dados = {'email': 'invalido', 'senha': 'senha123'}
    resposta = cliente.post('/cadastro', json=dados)
    # Somente se você decidir validar email formatado
    assert resposta.status_code in [400, 201]
