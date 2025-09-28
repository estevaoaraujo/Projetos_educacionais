# Arquivo: MY_MONEY/routes/login.py

from flask import Blueprint, request, render_template, make_response, redirect, url_for, g, flash, jsonify
# Mantenha as importações de auth_backend e decorator
from auth.auth_backend import registrar_usuario, autenticar_e_gerar_token
from auth.decorator import login_requerido

# Importe as funções de banco de dados que usam g.db
# Remova a importação de conectar_db
from database.database import limpar_token_usuario_por_id, obter_resumo_usuario # Estes nomes devem existir em database.py e usar g.db
# Remova importar session se não estiver usando
import re
from flask import jsonify, request
from auth.auth_backend import registrar_usuario


import jwt
import logging # Importe logging aqui também

login_route = Blueprint('login_route', __name__)

@login_route.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Detecta se a requisição é JSON
        if request.is_json:
            dados = request.get_json()
            email = dados.get('email')
            senha = dados.get('senha')
        else:
            email = request.form.get('email')
            senha = request.form.get('senha')

        token = autenticar_e_gerar_token(email, senha)

        if token:
            if request.is_json:
                return {'token': token}, 200  # resposta para API/testes
            else:
                resp = make_response(redirect(url_for('dashboard_route.dashboard')))
                resp.set_cookie('token', token, httponly=True, samesite='Lax')
                return resp
        else:
            if request.is_json:
                return {'erro': 'Credenciais inválidas'}, 401
            else:
                flash("Credenciais inválidas", "danger")
                return render_template("login.html")

    return render_template("login.html")



@login_route.route('/cadastro', methods=['GET', 'POST'])
def cadastro_page():
    if request.method == 'POST':
        if request.is_json:
            dados = request.get_json()
            email = dados.get('email')
            senha = dados.get('senha')
        else:
            email = request.form.get('email')
            senha = request.form.get('senha')

        if not email or not senha:
            if request.is_json:
                return {'erro': 'Email e senha obrigatórios'}, 400
            flash("Email e senha obrigatórios", "danger")
            return render_template("cadastro.html")

        if registrar_usuario(email, senha):
            if request.is_json:
                return {'mensagem': 'Usuário registrado com sucesso'}, 201
            flash("Usuário cadastrado com sucesso! Faça login.", "success")
            return redirect(url_for('login_route.login'))
        else:
            if request.is_json:
                return {'erro': 'Usuário já existe'}, 400
            flash("Usuário já existe. Tente outro email.", "danger")
            return render_template("cadastro.html")

    return render_template("cadastro.html")


def validar_email(email):
    padrao = r'^\S+@\S+\.\S+$'
    return re.match(padrao, email) is not None

@login_route.route('/register', methods=['POST'])
def register_api():
    if not request.is_json:
        return jsonify({'erro': 'A requisição deve ser JSON'}), 400

    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
    if not validar_email(email):
        return jsonify({'erro': 'Email inválido'}), 400

    if registrar_usuario(email, senha):
        return jsonify({'mensagem': 'Usuário registrado com sucesso'}), 201
    return jsonify({'erro': 'Usuário já existe'}), 400

@login_route.route('/logout')
def logout():
    token = request.cookies.get('token')

    if token:
        try:
            payload = jwt.decode(token, "chave_super_secreta", algorithms=['HS256'])
            # limpar_token_usuario_por_id (em database.py) agora usa g.db internamente
            limpar_token_usuario_por_id(payload['usuario_id']) # Chama a função adaptada que usa g.db
        except jwt.InvalidTokenError:
            pass
        except Exception as e:
            logging.error(f"Erro ao limpar token no logout: {e}")
            pass

    resp = make_response(redirect(url_for('login_route.login')))
    resp.set_cookie('token', '', max_age=0, expires=0, path='/', samesite='Lax', httponly=True)
    return resp