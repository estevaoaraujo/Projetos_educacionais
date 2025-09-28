# Arquivo: MY_MONEY/auth/auth_backend.py

import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import sqlite3 # Adicione esta linha

# Importe get_db e verificar_conexao do módulo de contexto
from database.db_context import get_db, verificar_conexao # Para obter a conexão do contexto e verificá-la
# Importe as funções de banco de dados adaptadas que USAM g.db
from database.database import registrar_usuario_db, limpar_token_usuario_por_id # Use os nomes que existem em database.py


SECRET_KEY = "chave_super_secreta"

# Restante do seu código...

def gerar_token(usuario_id):
    payload = {
        'usuario_id': usuario_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Adaptado para usar g.db
def verificar_usuario(email, senha): # Removido o parâmetro conexao
    conn = get_db() # Obtém a conexão do contexto
    if conn is None:
        logging.error("Falha ao obter conexão com o banco de dados em verificar_usuario")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE email=?", (email,))
        resultado = cursor.fetchone()
        if resultado:
            senha_hash = resultado[0]
            return check_password_hash(senha_hash, senha)
        return False
    except sqlite3.Error as e:
        logging.error(f"[ERRO AUTH] Falha ao verificar usuário {email}: {e}")
        return False
    # A conexão será fechada pelo teardown_request

# Adaptado para usar g.db e chamar registrar_usuario_db (que também usa g.db)
def registrar_usuario(email, senha): # Removido o parâmetro conexao
    conn = get_db() # Obtém a conexão do contexto
    if conn is None:
        logging.error("Falha ao obter conexão com o banco de dados em registrar_usuario")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE email=?", (email,))
        if cursor.fetchone():
            return False  # Usuário já existe

        senha_hash = generate_password_hash(senha)
        # Chama a função de baixo nível no database.py que faz a inserção (ela usará g.db)
        return registrar_usuario_db(email, senha_hash) # Não passa a conexão
    except sqlite3.Error as e:
         logging.error(f"[ERRO AUTH] Falha ao registrar usuário {email}: {e}")
         return False
    # A conexão será fechada pelo teardown_request

# Adaptado para usar g.db
def autenticar_e_gerar_token(email, senha): # Removido o parâmetro conexao
    conn = get_db() # Obtém a conexão do contexto
    if not verificar_conexao(conn): # Usando verificar_conexao do db_context
        logging.error("Conexão inválida em autenticar_e_gerar_token")
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, senha FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        if usuario:
            usuario_id, senha_hash = usuario
            if check_password_hash(senha_hash, senha):
                token = gerar_token(usuario_id)
                cursor.execute("UPDATE usuarios SET token = ? WHERE id = ?", (token, usuario_id))
                conn.commit()
                return token
    except sqlite3.Error as e:
        logging.error(f"[ERRO AUTH] Falha ao autenticar usuário {email}: {e}")
    # A conexão será fechada pelo teardown_request
    return None

def verificar_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
