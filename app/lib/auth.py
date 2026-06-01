# encoding: utf-8
from functools import wraps
from flask import session, redirect, request


def admin_required(f):
    """
    Decorator que protege rotas administrativas.
    Redireciona para /admin/login se não estiver autenticado como admin.

    Uso:
        from app.lib.auth import admin_required

        @SiteBlueprint.route('/products/products')
        @admin_required
        def product_get():
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(f'/admin/login?next={request.path}')
        return f(*args, **kwargs)
    return decorated


def client_required(f):
    """
    Decorator que protege rotas de cliente logado.
    Redireciona para /client/login se não estiver autenticado.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('client_id'):
            return redirect(f'/client/login?next={request.path}')
        return f(*args, **kwargs)
    return decorated
