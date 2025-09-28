# Arquivo: MY_MONEY/database/db_context.py

import sqlite3
import os
from flask import g
import logging # Importar logging aqui também

# Caminho absoluto para o banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'usuarios.db')

# Conecta ao banco de dados SQLite
def conectar_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Opcional: retorna linhas como dicionários/objetos
        # Desabilita o autocommit padrão para gerenciar transações manualmente (recomendado)
        conn.isolation_level = None
        return conn
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB_CONTEXT] Falha ao conectar ao banco de dados: {e}")
        return None

# Obtém a conexão do contexto da aplicação (g)
def get_db():
    if 'db' not in g:
        g.db = conectar_db()
    return g.db

# Fecha a conexão ao final da requisição
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logging.debug("Conexão do banco de dados fechada.") # Opcional: log para depuração

# Função auxiliar para verificar a conexão (pode ser útil em database.py)
def verificar_conexao(conn):
    if conn is None:
        logging.error("[ERRO DB_CONTEXT] Conexão com o banco de dados não estabelecida para verificação.")
        return False
    try:
        conn.execute("SELECT 1")
        return True
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB_CONTEXT] Erro ao verificar conexão: {e}")
        return False