import jwt
from functools import wraps
from flask import request, redirect, url_for, g, render_template

SECRET_KEY = "chave_super_secreta"

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('login_route.login'))

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.usuario_id = payload['usuario_id']
        except jwt.ExpiredSignatureError:
            # Redireciona para tela personalizada de token expirado
            return render_template("token_expirado.html"), 401
        except jwt.InvalidTokenError:
            return redirect(url_for('login_route.login'))

        return f(*args, **kwargs)

    return decorated_function

