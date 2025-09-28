# Arquivo: MY_MONEY/routes/dashboard.py

from flask import Blueprint, render_template, request, redirect, session, jsonify, g, flash, url_for
from datetime import datetime, timedelta
import logging # Adicione esta linha
# Importe get_db do módulo de contexto
from database.db_context import get_db

# Importe o decorador de autenticação
from auth.decorator import login_requerido


# Remova a importação de conectar_db (se ainda existir)
# from database.database import conectar_db

# Importe as funções de banco de dados adaptadas que usam g.db
# Você precisará adaptar estas funções em database.py para usar g.db ou receber conn
from database.database import (
    obter_resumo_usuario, # Usa g.db internamente
    salvar_lancamento_db, # Usa g.db internamente
    obter_categorias_db,  # Crie esta função em database.py usando g.db
    obter_tipos_pagamento_db, # Crie esta função em database.py usando g.db
    # calcular_saldo_db, # Esta função foi movida/adaptada, remova se ainda estiver aqui
    obter_lancamentos_db, # Adapte ou mova para database.py e use g.db
    excluir_lancamento_db # Adapte ou mova para database.py e use g.db
)
# Importe get_db se precisar passar a conexão para as funções que ainda não foram adaptadas
# from database.db_context import get_db # Remova ou mantenha apenas a importação acima

dashboard_route = Blueprint('dashboard_route', __name__)

# Configurar logging (pode ser feito uma vez em run.py)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# A função calcular_saldo agora deve estar em database.py e usar g.db ou receber conn
# Remova a definição local de calcular_saldo


@dashboard_route.route('/dashboard')
@login_requerido
def dashboard():
    # Obtenha a conexão do contexto (se as funções de database.py recebem conn)
    # conn = get_db()
    # if conn is None:
    #      flash("Erro ao conectar ao banco de dados.", "danger")
    #      return render_template("dashboard.html", resumo={})

    try:
        # Chame as funções de banco de dados adaptadas que usam g.db
        resumo = obter_resumo_usuario(g.usuario_id) # Usa g.db internamente
        categorias = obter_categorias_db() # Usa g.db internamente (adapte em database.py)
        tipos_pagamento = obter_tipos_pagamento_db() # Usa g.db internamente (adapte em database.py)

        # Os dados para o gráfico de pizza na carga inicial da página
        # também devem ser obtidos usando uma função adaptada que usa g.db
        # Ex: dados_por_categoria = obter_dados_pizza_dashboard(g.usuario_id)
        # Por enquanto, se você ainda usa o código na rota, obtenha a conexão de g:
        # conn = get_db()
        # cursor = conn.cursor()
        # cursor.execute(...) # SQL para dados_por_categoria usando g.usuario_id
        # dados_por_categoria = cursor.fetchall()

        # Se os dados_por_categoria são obtidos via AJAX, remova a consulta e passe [] inicialmente
        dados_por_categoria = [] # Assumindo que são carregados via AJAX

        mes_nome = datetime.now().strftime('%B').capitalize()
        ano = datetime.now().year
        titulo_mes = f"{mes_nome} {ano}"

        return render_template(
            'dashboard.html',
            resumo=resumo,
            categorias=categorias,
            tipos_pagamento=tipos_pagamento,
            dados_por_categoria=dados_por_categoria,
            titulo_mes=titulo_mes
        )
    except Exception as e:
        logging.error(f"Erro na rota /dashboard: {e}")
        flash("Ocorreu um erro ao carregar o dashboard.", "danger")
        return redirect(url_for('login_route.login'))

@dashboard_route.route('/salvar_lancamento', methods=['POST'])
@login_requerido
def salvar_lancamento():
    usuario_id = g.usuario_id
    categoria_id = request.form.get('categoria')
    tipo_pagamento_id = request.form.get('tipo_conta')
    produto_servico = request.form.get('produto_servico')
    valor = request.form.get('valor')
    data = request.form.get('data')
    descricao = request.form.get('descricao')
    tipo = request.form.get('tipo')

    # Chame a função adaptada que usa g.db
    if salvar_lancamento_db(usuario_id, categoria_id, tipo_pagamento_id, produto_servico, valor, data, descricao, tipo):
         return redirect('/dashboard?sucesso=1')
    else:
         flash("Erro ao salvar lançamento.", "danger") # Adicionar flash message para erro
         return redirect('/dashboard?erro=1') # Redirecionar com parâmetro de erro


@dashboard_route.route('/resumo_periodo')
@login_requerido
def resumo_periodo():
    usuario_id = g.usuario_id
    periodo = request.args.get('periodo', 'mes')

    logging.debug(f"Buscando resumo para usuario_id: {usuario_id}, periodo: {periodo}")

    if not usuario_id:
        logging.debug("usuario_id não encontrado em g.")
        return jsonify({
            'entradas': 0,
            'saidas': 0,
            'saldo': 0,
            'total_acumulado_entradas': 0,
            'total_acumulado_saidas': 0,
            'total_acumulado_saldo': 0
        })

    # Chame a função adaptada que usa g.db e aceita o período
    resumo_periodo_data = obter_resumo_usuario(usuario_id, periodo)
    entradas_periodo = resumo_periodo_data.get('entradas', 0)
    saidas_periodo = resumo_periodo_data.get('saidas', 0)
    saldo_periodo = entradas_periodo - saidas_periodo # Calcule o saldo do período com os dados filtrados

    # Calcular resumo total acumulado usando obter_resumo_usuario com periodo='total'
    resumo_total_acumulado = obter_resumo_usuario(usuario_id, periodo='total')
    total_acumulado_entradas = resumo_total_acumulado.get('entradas', 0)
    total_acumulado_saidas = resumo_total_acumulado.get('saidas', 0)
    total_acumulado_saldo = resumo_total_acumulado.get('saldo', 0)


    logging.debug(f"Resultados para {periodo}: Entradas={entradas_periodo}, Saídas={saidas_periodo}, Saldo={saldo_periodo}")
    logging.debug(f"Resultados Acumulados: Entradas={total_acumulado_entradas}, Saídas={total_acumulado_saidas}, Saldo={total_acumulado_saldo}")


    return jsonify({
        'entradas': entradas_periodo,
        'saidas': saidas_periodo,
        'saldo': saldo_periodo,
        'total_acumulado_entradas': total_acumulado_entradas,
        'total_acumulado_saidas': total_acumulado_saidas,
        'total_acumulado_saldo': total_acumulado_saldo
    })

@dashboard_route.route('/resumo_operacoes')
@login_requerido
def resumo_operacoes():
    usuario_id = g.usuario_id
    if not usuario_id:
        return jsonify([])

    # Chame a função adaptada que usa g.db (crie esta função em database.py)
    # Ex: dados_resumo = obter_resumo_operacoes_db(usuario_id)
    # Por enquanto, mantendo a lógica temporária na rota, mas usando get_db:
    conn = get_db()
    if conn is None:
        logging.error("Falha ao obter conexão para resumo_operacoes")
        return jsonify([])

    try:
        cursor = conn.cursor()
        mes_atual = datetime.now().strftime('%Y-%m')

        consulta = """
            SELECT
                c.nome AS categoria,
                SUM(CASE WHEN l.tipo = 'entrada' THEN l.valor ELSE 0 END) AS total_entrada,
                SUM(CASE WHEN l.tipo = 'saida' THEN l.valor ELSE 0 END) AS total_saida
            FROM lancamentos l
            JOIN categorias c ON l.categoria_id = c.id
            WHERE l.usuario_id = ? AND strftime('%Y-%m', l.data) = ?
            GROUP BY c.nome
            ORDER BY c.nome
        """
        parametros = (usuario_id, mes_atual)

        cursor.execute(consulta, parametros)
        dados_resumo = cursor.fetchall()
    except Exception as e:
         logging.error(f"Erro em resumo_operacoes: {e}")
         dados_resumo = []

    resultados = []
    for row in dados_resumo:
        resultados.append({
            "categoria": row[0],
            "total_entrada": row[1] or 0,
            "total_saida": row[2] or 0
        })

    return jsonify(resultados)

@dashboard_route.route('/entradas_saidas')
@login_requerido
def entradas_saidas():
    usuario_id = g.usuario_id
    if not usuario_id:
        return jsonify([])

    tipo_filtro = request.args.get('tipo_filtro')
    categoria_filtro = request.args.get('categoria_filtro')

    # Chame a função adaptada que usa g.db (crie esta função em database.py)
    # Ex: dados = obter_lancamentos_db(usuario_id, tipo_filtro, categoria_filtro)
    # Por enquanto, mantendo a lógica temporária na rota, mas usando get_db:
    conn = get_db()
    if conn is None:
        logging.error("Falha ao obter conexão para entradas_saidas")
        return jsonify([])

    try:
        cursor = conn.cursor()
        consulta = """
            SELECT l.id, c.nome AS categoria, l.produto_servico, t.descricao AS tipo_conta,
            l.valor, l.data, l.tipo
            FROM lancamentos l
            JOIN categorias c ON l.categoria_id = c.id
            JOIN tipos_pagamento t ON l.tipo_conta_id = t.id -- Verifique se o nome da coluna está correto (tipo_conta_id ou tipo_pagamento_id)
            WHERE l.usuario_id = ?
        """
        parametros = (usuario_id,)

        if tipo_filtro:
            consulta += " AND l.tipo = ?"
            parametros += (tipo_filtro,)

        if categoria_filtro:
            consulta += " AND l.categoria_id = ?"
            parametros += (categoria_filtro,)

        consulta += " ORDER BY l.data DESC"

        cursor.execute(consulta, parametros)
        dados = cursor.fetchall()
    except Exception as e:
         logging.error(f"Erro em entradas_saidas: {e}")
         dados = []


    resultados = [
        {
            "id": row[0],
            "categoria": row[1],
            "produto_servico": row[2],
            "tipo_conta": row[3],
            "valor": row[4],
            "data": row[5],
            "tipo": row[6]
        }
        for row in dados
    ]

    return jsonify(resultados)

@dashboard_route.route('/distribuicao_financeira')
@login_requerido
def distribuicao_financeira():
    usuario_id = g.usuario_id
    periodo = request.args.get('periodo', 'mes')
    if not usuario_id:
        return jsonify([])

    conn = get_db()
    if conn is None:
        logging.error("Falha ao obter conexão para distribuicao_financeira")
        return jsonify([])

    try:
        cursor = conn.cursor()
        consulta = """
            SELECT categorias.nome, SUM(lancamentos.valor)
            FROM lancamentos
            JOIN categorias ON lancamentos.categoria_id = categorias.id
            WHERE lancamentos.tipo = 'saida' AND lancamentos.usuario_id = ?
        """
        parametros = [usuario_id]

        if periodo == 'semana':
            inicio_semana = datetime.now().date() - timedelta(days=datetime.now().weekday())
            fim_semana = inicio_semana + timedelta(days=6)
            consulta += " AND lancamentos.data BETWEEN ? AND ?"
            parametros.extend([inicio_semana.strftime('%Y-%m-%d'), fim_semana.strftime('%Y-%m-%d')])
        elif periodo == 'ano':
            consulta += " AND strftime('%Y', lancamentos.data) = ?"
            parametros.append(datetime.now().strftime('%Y'))
        else:  # mes
            consulta += " AND strftime('%Y-%m', lancamentos.data) = ?"
            parametros.append(datetime.now().strftime('%Y-%m'))

        consulta += " GROUP BY categorias.nome"

        logging.debug(f"Consulta SQL para distribuicao_financeira ({periodo}): {consulta}")
        logging.debug(f"Parâmetros para distribuicao_financeira ({periodo}): {parametros}")

        cursor.execute(consulta, parametros)
        dados = cursor.fetchall()

        logging.debug(f"Dados brutos do DB para distribuicao_financeira ({periodo}): {dados}")

    except Exception as e:
        logging.error(f"Erro em distribuicao_financeira: {e}")
        dados = []

    resultados = []
    for row in dados:
        resultados.append({
            "categoria": row[0],
            "valor": row[1] or 0
        })

    return jsonify(resultados)

@dashboard_route.route('/entradas_saidas_mensal')
@login_requerido
def entradas_saidas_mensal():
    usuario_id = g.usuario_id
    if not usuario_id:
        return jsonify([])

    conn = get_db()
    if conn is None:
        logging.error("Falha ao obter conexão para entradas_saidas_mensal")
        return jsonify([])

    try:
        cursor = conn.cursor()

        consulta = """
            SELECT strftime('%Y-%m', data) as mes,
                SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END) AS total_entradas,
                SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END) AS total_saidas
            FROM lancamentos
            WHERE usuario_id = ?
            GROUP BY mes
            ORDER BY mes
        """
        cursor.execute(consulta, (usuario_id,))
        dados = cursor.fetchall()

        resultados = [
            {
                "mes": row[0],
                "entradas": row[1],
                "saidas": row[2]
            }
            for row in dados
        ]

    except Exception as e:
        logging.error(f"Erro em entradas_saidas_mensal: {e}")
        resultados = []

    return jsonify(resultados)



@dashboard_route.route('/excluir_lancamento', methods=['POST'])
@login_requerido
def excluir_lancamento():
    usuario_id = g.usuario_id
    lancamento_id = request.form.get('lancamento_id')
    if not usuario_id or not lancamento_id:
        return jsonify({'success': False, 'message': 'Usuário ou lançamento não encontrado'})

    # Chame a função adaptada que usa g.db (crie esta função em database.py)
    # Ex: sucesso = excluir_lancamento_db(lancamento_id, usuario_id)
    # Por enquanto, mantendo a lógica temporária na rota, mas usando get_db:
    conn = get_db()
    if conn is None:
        logging.error("Falha ao obter conexão para excluir_lancamento")
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'})

    try:
        cursor = conn.cursor()
        # Adicionado verificação de usuario_id para segurança
        cursor.execute("DELETE FROM lancamentos WHERE id = ? AND usuario_id = ?", (lancamento_id, usuario_id))
        conn.commit()
        # Verifica se alguma linha foi afetada
        if cursor.rowcount > 0:
             return jsonify({'success': True, 'message': 'Lançamento excluído com sucesso'})
        else:
             # Nenhuma linha afetada pode significar que o lançamento não existe ou não pertence ao usuário
             return jsonify({'success': False, 'message': 'Lançamento não encontrado ou você não tem permissão.'})
    except Exception as e:
        logging.error(f"Erro ao excluir lançamento {lancamento_id} para o usuário {usuario_id}: {e}")
        return jsonify({'success': False, 'message': 'Erro interno ao excluir lançamento.'})


@dashboard_route.route('/extrato')
@login_requerido
def extrato():
    # Obter categorias para o filtro na página de extrato
    # Chame a função adaptada que usa g.db (crie esta função em database.py)
    # Ex: categorias = obter_categorias_db()
    # Por enquanto, mantendo a lógica temporária na rota, mas usando get_db:
    conn = get_db()
    categorias = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, tipo FROM categorias") # Assumindo categorias globais
            categorias = cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao carregar categorias para extrato: {e}")
    # Não feche a conexão aqui!

    return render_template('extrato.html', categorias=categorias)