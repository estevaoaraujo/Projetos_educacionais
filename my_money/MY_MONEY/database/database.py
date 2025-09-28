# Arquivo: MY_MONEY/database/database.py

import sqlite3
import logging
# Importe get_db, verificar_conexao e conectar_db do seu módulo de contexto (db_context.py)
from database.db_context import get_db, verificar_conexao, conectar_db
from datetime import datetime, timedelta # Adicione esta linha


# Configurar logging (se ainda não estiver configurado globalmente em run.py)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


# Funções de criação de tabela adaptadas para receber conexão E COM O SQL CORRETO
def criar_tabela_usuarios_db(conn):
    """Cria a tabela de usuários se ela não existir."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            token TEXT
        )
    ''')
    # Não chame conn.commit() aqui individualmente se estiver usando BEGIN/COMMIT na função chamadora (criar_todas_tabelas)


def criar_tabela_lancamentos_db(conn):
    """Cria a tabela de lançamentos se ela não existir."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            categoria_id INTEGER,
            tipo_conta_id INTEGER,
            tipo TEXT CHECK(tipo IN ('entrada', 'saida')) NOT NULL,
            produto_servico TEXT,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (tipo_conta_id) REFERENCES tipos_pagamento(id)
        )
    ''')
    # conn.commit() # Remova


def criar_tabela_categorias_db(conn):
    """Cria a tabela de categorias se ela não existir."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('entrada', 'saida'))
            -- usuario_id INTEGER -- Adicione se categorias forem por usuário, com FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    # conn.commit() # Remova


def criar_tabela_tipos_pagamento_db(conn):
    """Cria a tabela de tipos de pagamento se ela não existir."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_pagamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL
            -- usuario_id INTEGER -- Adicione se tipos de pagamento forem por usuário, com FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    # conn.commit() # Remova


# ** FUNÇÃO PRINCIPAL PARA CRIAR TODAS AS TABELAS **
# Esta função conecta e fecha a conexão APENAS para a criação inicial do banco.
def criar_todas_tabelas():
    """Cria todas as tabelas no banco de dados se elas não existirem."""
    conn = conectar_db() # Usa conectar_db APENAS AQUI para a criação inicial
    if not verificar_conexao(conn):
        print("Não foi possível criar as tabelas do banco de dados: Falha na conexão.")
        return

    try:
        conn.execute("BEGIN") # Inicia uma transação explícita (opcional, mas boa prática)
        criar_tabela_usuarios_db(conn) # Chama as funções adaptadas, passando a conexão
        criar_tabela_lancamentos_db(conn)
        criar_tabela_categorias_db(conn)
        criar_tabela_tipos_pagamento_db(conn)
        conn.commit() # Comita a transação se tudo deu certo
        print("Tabelas verificadas/criadas com sucesso.")
    except sqlite3.Error as e:
         print(f"Erro ao criar tabelas: {e}")
         conn.rollback() # Desfaz as operações se houver erro na criação
    finally:
        conn.close() # Fecha a conexão APÓS a criação


# ** Funções de Operação de Banco de Dados adaptadas para USAR g.db **
# Elas obtêm a conexão de g.db usando get_db() e NÃO a fecham.
# Mantenha os nomes originais (sem _db no final) para evitar quebrar imports existentes.

# Cadastra um novo usuário - AGORA USA get_db()
def registrar_usuario_db(email, senha_hash):
    """Insere um novo usuário no banco de dados."""
    conn = get_db() # Obtém a conexão de g.db
    if conn is None: # Pode manter a verificação ou confiar que get_db loga o erro
        logging.error("Conexão inválida em registrar_usuario_db")
        return False
    try:
        cursor = conn.cursor()
        # A verificação de usuário existente DEVE estar em auth/auth_backend.py
        # Esta função em database.py deve apenas INSERIR.
        cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha_hash))
        conn.commit() # Commit da transação
        return True
    except sqlite3.IntegrityError: # Captura erro de UNIQUE constraint (email duplicado)
        logging.error(f"[ERRO DB] Tentativa de registrar email duplicado: {email}")
        # Não precisa de rollback se isolation_level=None no db_context.py
        return False
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao registrar usuário {email}: {e}")
        # conn.rollback() # Se usar BEGIN/COMMIT/ROLLBACK explícito em operações CRUD
        return False
    # Não feche a conexão aqui!


# Limpa o token do usuário por ID - AGORA USA get_db()
def limpar_token_usuario_por_id(usuario_id):
    """Define o token de um usuário como NULL no banco de dados."""
    conn = get_db() # Obtém a conexão de g.db
    if conn is None:
        logging.error("Conexão inválida em limpar_token_usuario_por_id")
        return
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET token = NULL WHERE id = ?", (usuario_id,))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao limpar token para o usuário {usuario_id}: {e}")
    # Não feche a conexão aqui!


# Função para obter resumo do usuário - AGORA USA get_db() E ACEITA PERÍODO
def obter_resumo_usuario(usuario_id, periodo='total'):
    """Obtém o resumo financeiro (entradas, saídas, saldo) de um usuário para um período específico."""
    conn = get_db() # Obtém a conexão de g.db
    if conn is None:
         logging.error("Conexão inválida em obter_resumo_usuario")
         return {}

    try:
        cursor = conn.cursor()

        # Construir a cláusula WHERE para filtrar por período
        where_clause = "WHERE usuario_id=?"
        parametros = [usuario_id]

        if periodo == 'semana':
            # Calcula o início da semana atual
            today = datetime.now()
            start_of_week = today.date() - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            where_clause += " AND data BETWEEN ? AND ?"
            parametros.extend([start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')])
        elif periodo == 'mes':
            # Filtra pelo mês e ano atuais
            today = datetime.now()
            where_clause += " AND strftime('%Y-%m', data) = ?"
            parametros.append(today.strftime('%Y-%m'))
        elif periodo == 'ano':
            # Filtra pelo ano atual
            today = datetime.now()
            where_clause += " AND strftime('%Y', data) = ?"
            parametros.append(today.strftime('%Y'))
        # Se periodo for 'total' (padrão), a cláusula WHERE original já filtra por usuario_id

        # Consulta para total de entradas
        cursor.execute(f"SELECT COALESCE(SUM(valor), 0) FROM lancamentos {where_clause} AND tipo='entrada'", parametros)
        total_entradas = cursor.fetchone()[0]

        # Consulta para total de saídas
        cursor.execute(f"SELECT COALESCE(SUM(valor), 0) FROM lancamentos {where_clause} AND tipo='saida'", parametros)
        total_saidas = cursor.fetchone()[0]

        saldo = total_entradas - total_saidas

        # Para obter o email, não precisamos do filtro de período, pois é um dado do usuário
        cursor.execute("SELECT email FROM usuarios WHERE id=?", (usuario_id,))
        email_result = cursor.fetchone()
        email = email_result[0] if email_result else "Email não encontrado"

        return {
            'email': email,
            'entradas': total_entradas,
            'saidas': total_saidas,
            'saldo': saldo
        }
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao obter resumo do usuário {usuario_id} para o período {periodo}: {e}")
        return {}
    except Exception as e:
         logging.error(f"[ERRO DB] Erro inesperado ao obter resumo do usuário {usuario_id} para o período {periodo}: {e}")
         return {}
    # Não feche a conexão aqui!


# Adapte todas as outras funções de CRUD e consulta de forma semelhante
# (salvar_lancamento, obter_lancamentos, excluir_lancamento, obter_categorias, obter_tipos_pagamento,
# salvar_categoria, atualizar_categoria, excluir_categoria, salvar_tipo_pagamento, atualizar_tipo_pagamento, excluir_tipo_pagamento)
# para usar get_db() e não fechar a conexão.

# Exemplo para salvar lançamento - AGORA USA get_db()
def salvar_lancamento_db(usuario_id, categoria_id, tipo_pagamento_id, produto_servico, valor, data, descricao, tipo):
    """Salva um novo lançamento no banco de dados."""
    conn = get_db()
    if not verificar_conexao(conn):
        logging.error("Conexão inválida em salvar_lancamento_db")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lancamentos (
                usuario_id, categoria_id, tipo_conta_id, produto_servico, valor, data, descricao, tipo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (usuario_id, categoria_id, tipo_pagamento_id, produto_servico, valor, data, descricao, tipo))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao salvar lançamento: {e}")
        # conn.rollback()
        return False

# Exemplo para obter lançamentos (extrato) - AGORA USA get_db()
def obter_lancamentos_db(usuario_id, tipo_filtro=None, categoria_filtro=None):
    """Obtém lançamentos filtrados para um usuário."""
    conn = get_db()
    if not verificar_conexao(conn):
        logging.error("Conexão inválida em obter_lancamentos_db")
        return []
    cursor = conn.cursor()

    consulta = """
       SELECT l.id, c.nome AS categoria, l.produto_servico, t.descricao AS tipo_conta,
       l.valor, l.data, l.tipo
       FROM lancamentos l
       JOIN categorias c ON l.categoria_id = c.id
       JOIN tipos_pagamento t ON l.tipo_conta_id = t.id -- Verifique o nome da coluna aqui se necessário
       WHERE l.usuario_id = ?
    """
    parametros = [usuario_id] # Use lista para facilitar append

    if tipo_filtro and tipo_filtro != 'todos':
        consulta += " AND l.tipo = ?"
        parametros.append(tipo_filtro)

    if categoria_filtro and categoria_filtro != 'todas':
        consulta += " AND l.categoria_id = ?"
        parametros.append(categoria_filtro)

    consulta += " ORDER BY l.data DESC"

    try:
        cursor.execute(consulta, parametros)
        dados = cursor.fetchall()
        return dados
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao obter lançamentos para o usuário {usuario_id}: {e}")
        return []

# Exemplo para excluir lançamento - AGORA USA get_db()
def excluir_lancamento_db(lancamento_id, usuario_id): # Ajustado ordem dos parâmetros para consistência
    """Exclui um lançamento pelo ID, verificando se pertence ao usuário."""
    conn = get_db()
    if not verificar_conexao(conn):
        logging.error("Conexão inválida em excluir_lancamento_db")
        return False
    try:
        cursor = conn.cursor()
        # Adicionado verificação de usuario_id para segurança
        cursor.execute("DELETE FROM lancamentos WHERE id = ? AND usuario_id = ?", (lancamento_id, usuario_id))
        conn.commit()
        # Verifica se alguma linha foi afetada
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao excluir lançamento {lancamento_id} para o usuário {usuario_id}: {e}")
        return False

# Funções para obter categorias e tipos de pagamento - AGORA USAM get_db()
def obter_categorias_db():
    """Obtém todas as categorias."""
    conn = get_db()
    if not verificar_conexao(conn):
        logging.error("Conexão inválida em obter_categorias_db")
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, tipo FROM categorias") # Assumindo categorias globais
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao obter categorias: {e}")
        return []

def obter_tipos_pagamento_db():
    """Obtém todos os tipos de pagamento."""
    conn = get_db()
    if not verificar_conexao(conn):
        logging.error("Conexão inválida em obter_tipos_pagamento_db")
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, descricao FROM tipos_pagamento") # Assumindo tipos de pagamento globais
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao obter tipos de pagamento: {e}")
        return []

# Funções para salvar/atualizar/excluir categorias e tipos de pagamento - AGORA USAM get_db()
def salvar_categoria_db(nome, tipo, usuario_id=None):
    """Salva uma nova categoria."""
    conn = get_db()
    if not verificar_conexao(conn): return False
    try:
        cursor = conn.cursor()
        # Se categorias forem por usuário, inclua usuario_id na query
        if usuario_id is not None:
            cursor.execute("INSERT INTO categorias (nome, tipo, usuario_id) VALUES (?, ?, ?)", (nome, tipo, usuario_id))
        else:
             cursor.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", (nome, tipo))

        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"[ERRO DB] Falha ao salvar categoria {nome}: {e}")
        return False

def atualizar_categoria_db(id_categoria, novo_nome, usuario_id=None):
     """Atualiza o nome de uma categoria existente."""
     conn = get_db()
     if not verificar_conexao(conn): return False
     try:
         cursor = conn.cursor()
         # Adicionado verificação de usuario_id para segurança se categorias forem por usuário
         if usuario_id is not None:
             cursor.execute("UPDATE categorias SET nome = ? WHERE id = ? AND usuario_id = ?", (novo_nome, id_categoria, usuario_id))
         else:
             cursor.execute("UPDATE categorias SET nome = ? WHERE id = ?", (novo_nome, id_categoria))

         conn.commit()
         return cursor.rowcount > 0 # Retorna True se atualizou algo
     except sqlite3.Error as e:
         logging.error(f"[ERRO DB] Falha ao atualizar categoria {id_categoria}: {e}")
         return False

def excluir_categoria_db(id_categoria, usuario_id=None):
     """Exclui uma categoria existente."""
     conn = get_db()
     if not verificar_conexao(conn): return False
     try:
         cursor = conn.cursor()
         # Adicionado verificação de usuario_id para segurança se categorias forem por usuário
         if usuario_id is not None:
              cursor.execute("DELETE FROM categorias WHERE id = ? AND usuario_id = ?", (id_categoria, usuario_id))
         else:
              cursor.execute("DELETE FROM categorias WHERE id = ?", (id_categoria,))
         conn.commit()
         return cursor.rowcount > 0 # Retorna True se excluiu algo
     except sqlite3.Error as e:
         logging.error(f"[ERRO DB] Falha ao excluir categoria {id_categoria}: {e}")
         return False

def salvar_tipo_pagamento_db(descricao, usuario_id=None):
     """Salva um novo tipo de pagamento."""
     conn = get_db()
     if not verificar_conexao(conn): return False
     try:
         cursor = conn.cursor()
          # Se tipos de pagamento forem por usuário, inclua usuario_id na query
         if usuario_id is not None:
             cursor.execute("INSERT INTO tipos_pagamento (descricao, usuario_id) VALUES (?, ?)", (descricao, usuario_id))
         else:
              cursor.execute("INSERT INTO tipos_pagamento (descricao) VALUES (?)", (descricao,))
         conn.commit()
         return True
     except sqlite3.Error as e:
         logging.error(f"[ERRO DB] Falha ao salvar tipo de pagamento {descricao}: {e}")
         return False

def actualizar_tipo_pagamento_db(id_tipo, novo_tipo, usuario_id=None):
     """Atualiza a descrição de um tipo de pagamento existente."""
     conn = get_db()
     if not verificar_conexao(conn): return False
     try:
         cursor = conn.cursor()
         # Adicionado verificação de usuario_id para segurança se tipos de pagamento forem por usuário
         if usuario_id is not None:
             cursor.execute("UPDATE tipos_pagamento SET descricao = ? WHERE id = ? AND usuario_id = ?", (novo_tipo, id_tipo, usuario_id))
         else:
             cursor.execute("UPDATE tipos_pagamento SET descricao = ? WHERE id = ?", (novo_tipo, id_tipo))
         conn.commit()
         return cursor.rowcount > 0 # Retorna True se atualizou algo
     except sqlite3.Error as e:
         logging.error(f"[ERRO DB] Falha ao atualizar tipo de pagamento {id_tipo}: {e}")
         return False

def excluir_tipo_pagamento_db(id_tipo, usuario_id=None):
     """Exclui um tipo de pagamento existente."""
     conn = get_db()
     if not verificar_conexao(conn): return False
     try:
         cursor = conn.cursor()
         # Adicionado verificação de usuario_id para segurança se tipos de pagamento forem por usuário
         if usuario_id is not None:
              cursor.execute("DELETE FROM tipos_pagamento WHERE id = ? AND usuario_id = ?", (id_tipo, usuario_id))
         else:
              cursor.execute("DELETE FROM tipos_pagamento WHERE id = ?", (id_tipo,))
         conn.commit()
         return cursor.rowcount > 0 # Retorna True se excluiu algo
     except sqlite3.Error as e:
         logging.error(f"[ERRO DB] Falha ao excluir tipo de pagamento {id_tipo}: {e}")
         return False