# encoding: utf-8
from flask import render_template, make_response, request, redirect, session

from app.blueprints.site import SiteBlueprint
from app.model.users import ModelUser
from app.model.client import ModelClient
from app.model.enum import StatusEnum
from app import logging

LOGGER = logging.getLogger(__name__)


# ─── CLIENTE ────────────────────────────────────────────────────────────────

@SiteBlueprint.route('/client/login')
def login_get():
    if session.get('client_id'):
        next_url = request.args.get('next', '/')
        return redirect(next_url)
    next_url = request.args.get('next', '')
    resp = make_response(render_template('client/login.html',
        success=False,
        errors=None,
        data_input=None,
        next_url=next_url))
    resp.mimetype = 'text/html'
    return resp


@SiteBlueprint.route('/client/login', methods=['POST'])
def login_post():
    data = request.form.to_dict() or {}
    errors = {}

    # Suporta tanto 'email' (novo signup) quanto 'user_name' (formulário antigo)
    user_name = (data.get('email') or data.get('user_name') or '').strip().lower()
    # Suporta tanto 'password' (novo signup.html) quanto 'pwd' (formulário antigo)
    pwd = (data.get('password') or data.get('pwd') or '').strip()

    if not user_name:
        errors['user_name'] = ['E-mail obrigatório']
    if not pwd:
        errors['pwd'] = ['Senha obrigatória']

    if errors:
        resp = make_response(render_template('client/login.html',
            success=False,
            errors=errors,
            data_input=data))
        resp.mimetype = 'text/html'
        return resp

    try:
        user = ModelUser.query.filter_by(
            user_name=user_name,
            pwd=pwd,
            status=StatusEnum.enabled
        ).first()

        if user is None:
            resp = make_response(render_template('client/login.html',
                success=False,
                errors={'login': ['E-mail ou senha inválidos']},
                data_input=data))
            resp.mimetype = 'text/html'
            return resp

        client = ModelClient.query.filter_by(
            id=user.client_id,
            status=StatusEnum.enabled
        ).first()

        if client is None:
            resp = make_response(render_template('client/login.html',
                success=False,
                errors={'login': ['Cliente não encontrado ou inativo']},
                data_input=data))
            resp.mimetype = 'text/html'
            return resp

        # salva sessão do cliente
        session['client_id']    = client.id
        session['client_name']  = client.name
        session['client_email'] = client.email
        session['user_id']      = user.id
        session['role']         = 'client'

        next_url = request.args.get('next') or request.form.get('next') or '/'
        return redirect(next_url)

    except Exception as e:
        LOGGER.exception(e)
        resp = make_response(render_template('errors/500.html',
            success=False,
            errors=None))
        resp.mimetype = 'text/html'
        return resp, 500


# ─── ADMIN ───────────────────────────────────────────────────────────────────

@SiteBlueprint.route('/admin/login')
def admin_login_get():
    if session.get('role') == 'admin':
        return redirect('/admin')
    resp = make_response(render_template('admin/login.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp


@SiteBlueprint.route('/admin/login', methods=['POST'])
def admin_login_post():
    data = request.form.to_dict() or {}
    errors = {}

    user_name = data.get('user_name', '').strip()
    pwd = data.get('pwd', '').strip()

    if not user_name:
        errors['user_name'] = ['Usuário obrigatório']
    if not pwd:
        errors['pwd'] = ['Senha obrigatória']

    if errors:
        resp = make_response(render_template('admin/login.html',
            success=False,
            errors=errors,
            data_input=data))
        resp.mimetype = 'text/html'
        return resp

    try:
        # admin: usuário sem client_id (client_id IS NULL)
        # ajuste essa query se tiver uma tabela separada de admins
        user = ModelUser.query.filter_by(
            user_name=user_name,
            pwd=pwd,
            status=StatusEnum.enabled
        ).filter(
            ModelUser.client_id == None
        ).first()

        if user is None:
            resp = make_response(render_template('admin/login.html',
                success=False,
                errors={'login': ['Usuário ou senha inválidos']},
                data_input=data))
            resp.mimetype = 'text/html'
            return resp

        # salva sessão do admin
        session['user_id'] = user.id
        session['admin_name'] = user.user_name
        session['role'] = 'admin'

        return redirect('/admin')

    except Exception as e:
        LOGGER.exception(e)
        resp = make_response(render_template('errors/500.html',
            success=False,
            errors=None))
        resp.mimetype = 'text/html'
        return resp, 500


# ─── LOGOUT ──────────────────────────────────────────────────────────────────

@SiteBlueprint.route('/logout')
def logout():
    session.clear()
    return redirect('/')
