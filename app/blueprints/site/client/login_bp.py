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
        return redirect('/')
    resp = make_response(render_template('client/login.html',
        success=False,
        errors=None,
        data_input=None))
    resp.mimetype = 'text/html'
    return resp


@SiteBlueprint.route('/client/login', methods=['POST'])
def login_post():
    data = request.form.to_dict() or {}
    errors = {}

    user_name = data.get('user_name', '').strip()
    pwd = data.get('pwd', '').strip()

    if not user_name:
        errors['user_name'] = ['Usuário obrigatório']
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
                errors={'login': ['Usuário ou senha inválidos']},
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
        session['client_id'] = client.id
        session['client_name'] = client.name
        session['client_email'] = client.email
        session['user_id'] = user.id
        session['role'] = 'client'

        return redirect('/')

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
    return redirect('/client/login')
