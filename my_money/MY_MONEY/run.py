# Arquivo: MY_MONEY/run.py

from flask import Flask, redirect, g # Importe g aqui
from flask_cors import CORS
# Mantenha as importações dos blueprints
from routes.login import login_route
from routes.dashboard import dashboard_route
from routes.configuracao import configuracao_route

# Importe apenas criar_todas_tabelas de database.database
from database.database import criar_todas_tabelas
# Importe as funções de contexto do banco de dados
from database.db_context import get_db, close_db


app = Flask(__name__)
app.secret_key = "uma_chave_super_secreta"
CORS(app)

app.template_folder = 'templates'
app.static_folder = 'static'

# Defina as funções get_db e close_db (ou importe-as de db_context)
# Já estão definidas em db_context.py, então basta importá-las acima.

# Configure o teardown_request para fechar a conexão
@app.teardown_request
def handle_teardown_request(e=None):
    close_db(e)

# Registrando os blueprints
app.register_blueprint(dashboard_route)
app.register_blueprint(login_route)
app.register_blueprint(configuracao_route)

# Rota raiz redireciona para login
@app.route('/')
def home():
    return redirect("/login")

if __name__ == '__main__':
    criar_todas_tabelas()
    app.run(host='0.0.0.0', port=5000, debug=True)
