# encoding: utf-8
from urllib.parse import quote
from flask import render_template, request, session, redirect, url_for
from app.blueprints.site import SiteBlueprint
from app import db, logging
from app.model.products import ModelProduct
from app.model.order import ModelOrder
from app.model.order_item import ModelOrderItem
from app.model.client import ModelClient
from app.model.checkout import ModelCheckout
from app.model.enum import StatusEnum
from app.model.address import ModelAddress
from app.model.client_address import ModelClientAddress

LOGGER = logging.getLogger(__name__)

WHATSAPP_NUMBER = '5534984104546'
REQUIRED_FIELDS = ['email', 'zip_code', 'street', 'street_number', 'district', 'city', 'state']


def get_cart():
    return session.get('cart', {})


@SiteBlueprint.route('/cart/checkout', methods=['GET'])
def checkout_get():
    # Dentro da rota GET, após verificar o client_id na sessão:
    client_id = session.get('client_id')
    if client_id:
        address = ModelAddress.query.join(ModelClientAddress).filter(
            ModelClientAddress.client_id == client_id
        ).first()
        
        if address:
            session['client_address'] = {
                'zip_code':      address.zip_code,
                'street':        address.street,
                'street_number': address.street_number,
                'complement':    address.complement or '',
                'district':      address.district or '',
                'city':          address.city,
                'state':         address.state,
            }

    """Exibe o formulário de finalização do pedido."""
    cart = get_cart()
    if not cart:
        return redirect(url_for('SiteBlueprint.cart_get'))

    items, total = _build_items(cart)
    form_data = {}

    if session.get('client_id'):
        client = ModelClient.query.filter_by(
            id=session['client_id'],
            status=StatusEnum.enabled
        ).first()
        if client:
            form_data['email'] = client.email or ''

    return render_template('cart/checkout.html',
                           items=items,
                           total=total,
                           form_data=form_data)


@SiteBlueprint.route('/cart/checkout', methods=['POST'])
def checkout_post():
    """Processa o pedido: valida, salva na sessão e redireciona."""
    cart = get_cart()
    if not cart:
        return redirect(url_for('SiteBlueprint.cart_get'))

    data = request.form.to_dict()

    # Converte checkbox email_optin
    data['email_optin'] = data.get('email_optin') == '1'

    # Valida campos obrigatórios
    errors = {}
    for field in REQUIRED_FIELDS:
        if not data.get(field, '').strip():
            errors[field] = 'Campo obrigatório'

    if errors:
        items, total = _build_items(cart)
        return render_template('cart/checkout.html',
                               items=items, total=total,
                               errors=errors, form_data=data)

    # Salva dados na sessão para reaproveitar após login
    session['checkout_data'] = data

    # Se não logado, verifica se o email já tem cadastro
    if not session.get('client_id'):
        email = data.get('email', '').strip().lower()
        client_existente = ModelClient.query.filter_by(
            email=email,
            status=StatusEnum.enabled
        ).first()

        if client_existente:
            # Email já cadastrado — redireciona para login com mensagem
            return redirect('/client/login?next=/cart/checkout/confirm&email_exists=1')
        else:
            # Email novo — redireciona para cadastro
            return redirect('/client/signup?next=/cart/checkout/confirm')

    return _finalizar_pedido(data, cart)


@SiteBlueprint.route('/cart/checkout/confirm', methods=['GET'])
def checkout_confirm():
    """Chamado após login — finaliza o pedido com dados salvos na sessão."""
    if not session.get('client_id'):
        return redirect('/client/login?next=/cart/checkout/confirm')

    cart = get_cart()
    if not cart:
        return redirect(url_for('SiteBlueprint.cart_get'))

    data = session.get('checkout_data')
    if not data:
        return redirect(url_for('SiteBlueprint.checkout_get'))

    return _finalizar_pedido(data, cart)


# ── Lógica central de finalização ──

def _finalizar_pedido(data, cart):
    """Cria order, order_items e checkout no banco."""
    items, total = _build_items(cart)
    if not items:
        return redirect(url_for('SiteBlueprint.cart_get'))

    try:
        client_id = session['client_id']

        # 1. Cria o pedido
        model_order = ModelOrder()
        order = model_order.create_order({'client_id': client_id})
        if order is None:
            raise Exception('Erro ao criar pedido')

        # 2. Cria os itens do pedido
        for item in items:
            model_item = ModelOrderItem()
            result = model_item.create_order_item({
                'order_id':   order.id,
                'product_id': item['id'],
                'quantity':   item['quantity']
            })
            if result is None:
                raise Exception(f'Erro ao salvar item {item["name"]}')

        # 3. Salva o checkout no banco
        model_checkout = ModelCheckout()
        checkout = model_checkout.create_checkout({
            'order_id':      order.id,
            'client_id':     client_id,
            'email':         data.get('email', '').strip(),
            'email_optin':   data.get('email_optin', False),
            'zip_code':      data.get('zip_code', '').strip(),
            'street':        data.get('street', '').strip(),
            'street_number': data.get('street_number', '').strip(),
            'complement':    data.get('complement', '').strip() or None,
            'district':      data.get('district', '').strip(),
            'city':          data.get('city', '').strip(),
            'state':         data.get('state', '').strip().upper(),
            'notes':         data.get('notes', '').strip() or None,
            'payment_method': 'pix',
            'total_value':   total,
        })

        if checkout is None:
            LOGGER.error('Checkout errors: %s', model_checkout.errors)
            raise Exception(f'Erro ao salvar checkout: {model_checkout.errors}')

        # 4. Monta URL do WhatsApp
        msg = _build_whatsapp_message(data, items, total)
        whatsapp_url = f'https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={quote(msg)}'

        # 5. Limpa sessão e redireciona para PIX
        session.pop('cart', None)
        session.pop('checkout_data', None)
        session['pix_total']        = total
        session['pix_whatsapp_url'] = whatsapp_url

        return redirect(url_for('site_bp.pix_get', order_id=order.id))

    except Exception as e:
        LOGGER.exception(e)
        db.session.rollback()
        items, total = _build_items(cart)
        return render_template('cart/checkout.html',
                               items=items, total=total,
                               errors={'geral': 'Erro ao salvar pedido. Tente novamente.'},
                               form_data=data)


# ── Helpers ──

def _build_items(cart):
    """Busca produtos do banco com base no carrinho da sessão."""
    items = []
    total = 0.0
    for product_id, quantity in cart.items():
        product = ModelProduct.query.filter_by(
            id=int(product_id),
            status=StatusEnum.enabled
        ).first()
        if product:
            subtotal = float(product.value) * quantity
            total += subtotal
            items.append({
                'id':          product.id,
                'name':        product.name,
                'description': product.description,
                'value':       float(product.value),
                'path':        product.path,
                'quantity':    quantity,
                'subtotal':    subtotal
            })
    return items, total


def _build_whatsapp_message(data, items, total):
    """Monta a mensagem formatada para o WhatsApp."""
    lines = []
    lines.append('💎 *Novo Pedido - Aurora Semijóias*')
    lines.append('')
    lines.append(f'📧 *E-mail:* {data.get("email", "")}')

    end = f'{data.get("street", "")}, {data.get("street_number", "")}'
    if data.get('complement', '').strip():
        end += f' — {data["complement"]}'
    end += f'\n   {data.get("district", "")}, {data.get("city", "")}/{data.get("state", "").upper()}'
    end += f'\n   CEP {data.get("zip_code", "")}'
    lines.append(f'📍 *Endereço:*\n   {end}')

    if data.get('notes', '').strip():
        lines.append(f'📝 *Observações:* {data["notes"]}')

    lines.append('')
    lines.append('🛒 *Itens do Pedido:*')
    for item in items:
        lines.append(f'  • {item["name"]} × {item["quantity"]} — R$ {item["subtotal"]:.2f}')

    lines.append('')
    lines.append(f'💰 *Total: R$ {total:.2f}*')
    lines.append('')
    lines.append('_Pedido realizado pelo site Aurora Semijóias_')

    return '\n'.join(lines)
