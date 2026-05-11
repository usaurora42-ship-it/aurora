# encoding: utf-8
from flask import render_template, make_response, request, session, redirect

from app.blueprints.site import SiteBlueprint

from app import logging
from app.model.client import ModelClient
from app.model.phones import ModelPhone
from app.model.address import ModelAddress
from app.model.client_phone import ModelClientPhone
from app.model.client_address import ModelClientAddress
from app.model.users import ModelUser
from app.model.enum import StatusEnum

LOGGER = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Helpers de validação
# ─────────────────────────────────────────────

def _validate_step1(data):
    """Valida os campos obrigatórios da etapa 1."""
    errors = {}

    name = data.get('name', '').strip()
    if not name:
        errors['name'] = ['Nome é obrigatório.']
    elif len(name) > 80:
        errors['name'] = ['Nome deve ter no máximo 80 caracteres.']

    email = data.get('email', '').strip().lower()
    if not email:
        errors['email'] = ['E-mail é obrigatório.']
    elif len(email) > 150:
        errors['email'] = ['E-mail muito longo.']

    password = data.get('password', '')
    if not password:
        errors['password'] = ['Senha é obrigatória.']
    elif len(password) < 8:
        errors['password'] = ['A senha deve ter pelo menos 8 caracteres.']

    password_confirm = data.get('password_confirm', '')
    if password and password_confirm != password:
        errors['password_confirm'] = ['As senhas não coincidem.']

    if not data.get('terms'):
        errors['terms'] = ['Você deve aceitar os termos para continuar.']

    return errors


def _parse_phone(raw_phone):
    """Extrai código de área e número de um telefone brasileiro formatado."""
    digits = ''.join(filter(str.isdigit, raw_phone or ''))
    if len(digits) < 10:
        return None, None
    # Remove DDI 55 se vier junto
    if digits.startswith('55') and len(digits) >= 12:
        digits = digits[2:]
    code_area = digits[0:2]
    number    = digits[2:]
    return code_area, number


# ─────────────────────────────────────────────
#  GET /client/signup
# ─────────────────────────────────────────────

@SiteBlueprint.route('/client/signup')
def signup_get():
    from flask import session as flask_session

    # Pré-preenche com dados do checkout se vier de lá
    checkout_data = flask_session.get('checkout_data', {})
    data_input = None
    if checkout_data:
        data_input = {
            'email':   checkout_data.get('email', ''),
            'city':    checkout_data.get('city', ''),
            'state':   checkout_data.get('state', ''),
            'address': checkout_data.get('street', ''),
        }

    next_url = request.args.get('next', '/client/login')

    return make_response(render_template(
        'client/signup.html',
        success=False,
        errors=None,
        data_input=data_input,
        next_url=next_url
    ))


# ─────────────────────────────────────────────
#  POST /client/signup
# ─────────────────────────────────────────────

@SiteBlueprint.route('/client/signup', methods=['POST'])
def signup_post():
    data     = request.form.to_dict() or {}
    next_url = request.args.get('next') or data.get('next') or '/client/login'

    def render_error(errors):
        return make_response(render_template(
            'client/signup.html',
            success=False,
            errors=errors,
            data_input=data,
            next_url=next_url
        ))

    # ── 1. Valida campos obrigatórios ──────────────────────────────────────
    errors = _validate_step1(data)
    if errors:
        return render_error(errors)

    email = data['email'].strip().lower()
    name  = data['name'].strip()

    # ── 2. E-mail já cadastrado? ───────────────────────────────────────────
    if ModelClient.query.filter_by(email=email).first():
        return render_error({
            'email': ['Este e-mail já está cadastrado. Faça login ou use outro e-mail.']
        })

    # ── 3. Cria o cliente ──────────────────────────────────────────────────
    model_client = ModelClient()
    client = model_client.create_client({
        'name':  name,
        'email': email,
        'type':  'PF',          # pessoa física por padrão
    })

    if client is None:
        LOGGER.error('Erro ao criar cliente: %s', model_client.errors)
        return render_error(model_client.errors)

    # ── 4. Telefone (opcional) ─────────────────────────────────────────────
    raw_phone = data.get('phone', '').strip()
    if raw_phone:
        code_area, number = _parse_phone(raw_phone)
        if code_area and number:
            model_phone        = ModelPhone()
            model_client_phone = ModelClientPhone()

            # verifica se já existe
            phone = ModelPhone.query.with_entities(ModelPhone.id).filter_by(
                code_country='55',
                code_area=code_area,
                number=number,
                status=StatusEnum.enabled
            ).first()

            if phone is None:
                phone = model_phone.create_phone({
                    'code_country': '55',
                    'code_area':    code_area,
                    'number':       number,
                })

                if phone is None:
                    LOGGER.warning('Erro ao criar telefone: %s', model_phone.errors)
                    # não bloqueia o cadastro — só ignora o telefone
                else:
                    model_client_phone.create_client_phone({
                        'client_id': client.id,
                        'phone_id':  phone.id,
                    })

    # ── 5. Endereço (opcional) ─────────────────────────────────────────────
    #
    # O novo formulário envia campos simples (address, city, state).
    # O checkout envia campos detalhados (street, street_number, district,
    # zip_code, complement). Suportamos os dois formatos.
    #
    skip_optional = data.get('skip_optional')
    city  = data.get('city', '').strip()
    state = data.get('state', '').strip()

    # Monta o endereço apenas se tiver pelo menos cidade e estado
    if not skip_optional and city and state:
        from app.model.countries import ModelCountry
        model_address        = ModelAddress()
        model_client_address = ModelClientAddress()

        # Resolve campos que podem vir em dois formatos
        street      = data.get('street') or data.get('address') or ''
        street_num  = data.get('street_number', '')
        complement  = data.get('complement', '')
        district    = data.get('district', '')
        zip_code    = ''.join(filter(str.isdigit, data.get('zip_code', '')))

        country_id = ModelCountry().get_country_id('BRA')

        address = model_address.create_address({
            'state':         state,
            'city':          city,
            'district':      district,
            'zip_code':      zip_code,
            'street':        street,
            'street_number': street_num,
            'complement':    complement,
            'country_id':    country_id,
        })

        if address is None:
            LOGGER.warning('Erro ao criar endereço: %s', model_address.errors)
            # não bloqueia o cadastro
        else:
            model_client_address.create_client_address({
                'client_id':  client.id,
                'address_id': address.id,
            })

    # ── 6. Cria o usuário (login/senha) ───────────────────────────────────
    #
    # O novo HTML envia 'email' + 'password'.
    # O modelo ModelUser espera 'user_name' + 'pwd'.
    # Usamos o e-mail como user_name para simplificar — sem exigir
    # um campo separado de "nome de usuário".
    #
    model_user = ModelUser()

    # Verifica se já existe usuário para este cliente
    existing_user = ModelUser.query.with_entities(
        ModelUser.client_id
    ).filter_by(
        status=StatusEnum.enabled
    ).join(ModelClient).filter(
        ModelClient.id == client.id
    ).first()

    if existing_user is None:
        user = model_user.create_user({
            'client_id': client.id,
            'user_name': email,          # e-mail como username
            'pwd':       data['password'],
        })

        if user is None:
            LOGGER.error('Erro ao criar usuário: %s', model_user.errors)
            return render_error({'login': ['Erro ao criar acesso. Tente novamente.']})

    # ── 7. Salva nome na sessão e redireciona ─────────────────────────────
    session['name'] = name

    return redirect(next_url)
