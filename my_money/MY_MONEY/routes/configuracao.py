# Arquivo: MY_MONEY/routes/configuracao.py

from flask import Blueprint, render_template, request, redirect, session, g
# Remova a importação de conectar_db
# from database.database import conectar_db
import logging # Importe logging
# Importe as funções de banco de dados adaptadas que usam g.db
from database.database import (
    obter_categorias_db,
    obter_tipos_pagamento_db,
    salvar_categoria_db,
    atualizar_categoria_db,
    excluir_categoria_db,
    salvar_tipo_pagamento_db,
    actualizar_tipo_pagamento_db, # Corrigido nome para corresponder database.py
    excluir_tipo_pagamento_db
)
# Importe get_db se precisar passá-lo explicitamente para alguma função que ainda não foi adaptada
# from database.db_context import get_db

configuracao_route = Blueprint('configuracao_route', __name__)

# Configurar logging (pode ser feito uma vez em run.py)
# logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Página de configurações
@configuracao_route.route('/configuracao')
def configuracao():
    # Chame as funções de banco de dados adaptadas que usam g.db
    try:
        categorias = obter_categorias_db() # Usa g.db internamente
        tipos_pagamento = obter_tipos_pagamento_db() # Usa g.db internamente

        return render_template('configuracao.html', categorias=categorias, tipos_pagamento=tipos_pagamento)
    except Exception as e:
        logging.error(f"Erro ao carregar página de configuração: {e}")
        # Redirecionar ou mostrar mensagem de erro
        return render_template('configuracao.html', categorias=[], tipos_pagamento=[], error="Erro ao carregar dados de configuração.")


# Salvar categoria
@configuracao_route.route('/salvar_categoria', methods=['POST'])
def salvar_categoria():
    nome = request.form.get('nome_categoria')
    tipo = request.form.get('tipo_categoria')
    # usuario_id = g.usuario_id # Se categorias forem por usuário

    # Chame a função de banco de dados adaptada que usa g.db
    # Passe usuario_id se categorias forem por usuário
    if salvar_categoria_db(nome, tipo): # Adicione usuario_id aqui se necessário
        # Adicionar flash message de sucesso
         pass # Flash message para sucesso
    else:
        # Adicionar flash message de erro
        logging.error(f"Falha ao salvar categoria: {nome}, Tipo: {tipo}")
        pass # Flash message para erro

    return redirect('/configuracao')


# Atualizar categoria
@configuracao_route.route('/atualizar_categoria', methods=['POST'])
def atualizar_categoria():
    id_categoria = request.form.get('id_categoria')
    novo_nome = request.form.get('novo_nome')
    # usuario_id = g.usuario_id # Se categorias forem por usuário

    # Chame a função de banco de dados adaptada que usa g.db
    # Passe usuario_id se categorias forem por usuário
    if atualizar_categoria_db(id_categoria, novo_nome): # Adicione usuario_id aqui se necessário
         pass # Flash message para sucesso
    else:
         logging.error(f"Falha ao atualizar categoria: {id_categoria}, Novo Nome: {novo_nome}")
         pass # Flash message para erro

    return redirect('/configuracao')

# Salvar tipo de pagamento
@configuracao_route.route('/salvar_tipo_pagamento', methods=['POST'])
def salvar_tipo_pagamento():
    descricao = request.form.get('tipo_pagamento') # Corrigido nome da variável
    # usuario_id = g.usuario_id # Se tipos de pagamento forem por usuário

    # Chame a função de banco de dados adaptada que usa g.db
    # Passe usuario_id se tipos de pagamento forem por usuário
    if salvar_tipo_pagamento_db(descricao): # Adicione usuario_id aqui se necessário
        pass # Flash message para sucesso
    else:
        logging.error(f"Falha ao salvar tipo de pagamento: {descricao}")
        pass # Flash message para erro

    return redirect('/configuracao')

# Atualizar tipo de pagamento
@configuracao_route.route('/atualizar_tipo_pagamento', methods=['POST'])
def atualizar_tipo_pagamento():
    id_tipo = request.form.get('id_tipo')
    novo_tipo = request.form.get('novo_tipo')
    # usuario_id = g.usuario_id # Se tipos de pagamento forem por usuário

    # Chame a função de banco de dados adaptada que usa g.db
    # Passe usuario_id se tipos de pagamento forem por usuário
    if actualizar_tipo_pagamento_db(id_tipo, novo_tipo): # Adicione usuario_id aqui se necessário (Corrigido nome da função)
        pass # Flash message para sucesso
    else:
        logging.error(f"Falha ao atualizar tipo de pagamento: {id_tipo}, Novo Tipo: {novo_tipo}")
        pass # Flash message para erro

    return redirect('/configuracao')

#Excluir categoria
@configuracao_route.route('/excluir_categoria', methods=['POST'])
def excluir_categoria():
    id_categoria = request.form.get('id_categoria')
    # usuario_id = g.usuario_id # Se categorias forem por usuário

    # Chame a função de banco de dados adaptada que usa g.db
    # Passe usuario_id se categorias forem por usuário
    if excluir_categoria_db(id_categoria): # Adicione usuario_id aqui se necessário
        pass # Flash message para sucesso
    else:
         logging.error(f"Falha ao excluir categoria: {id_categoria}")
         pass # Flash message para erro

    return redirect('/configuracao')

#Excluir Pagamento
@configuracao_route.route('/excluir_tipo_pagamento', methods=['POST'])
def excluir_tipo_pagamento():
    id_tipo = request.form.get('id_tipo')
    # usuario_id = g.usuario_id # Se tipos de pagamento forem por usuário

    # Chame a função de banco de dados adaptada que usa g.db
    # Passe usuario_id se tipos de pagamento forem por usuário
    if excluir_tipo_pagamento_db(id_tipo): # Adicione usuario_id aqui se necessário
        pass # Flash message para sucesso
    else:
        logging.error(f"Falha ao excluir tipo de pagamento: {id_tipo}")
        pass # Flash message para erro

    return redirect('/configuracao')