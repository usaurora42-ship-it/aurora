# encoding: utf-8
from urllib.parse import quote
from flask import render_template, request, session, redirect, url_for
from app.blueprints.site import SiteBlueprint
from app import db, logging
from app.model.products import ModelProduct
from app.model.order import ModelOrder
from app.model.order_item import ModelOrderItem
from app.model.client import ModelClient
from app.model.enum import StatusEnum

LOGGER = logging.getLogger(__name__)

# Número do WhatsApp da Aurora (com DDI, sem símbolos)
WHATSAPP_NUMBER = '5534984104546'


def get_cart():
    return session.get('cart', {})


@SiteBlueprint.route('/cart/checkout', methods=['GET'])
def checkout_get():
    """Exibe o formulário de finalização do pedido."""
    cart = get_cart()

    if not cart:
        return redirect(url_for('SiteBlueprint.cart_get'))

    items, total = _build_items(cart)

    client_address = None
    client_data = {}

    if session.get('client_id'):
        # busca dados do cliente
        client = ModelClient.query.filter_by(
            id=session['client_id'],
            status=StatusEnum.enabled
        ).first()

        if client:
            # busca telefone do cliente
            from app.model.phones import ModelPhone
            from app.model.client_phone import ModelClientPhone
            phone = ModelPhone.query.join(ModelClientPhone).filter(
                ModelClientPhone.client_id == client.id,
                ModelPhone.status == StatusEnum.enabled
            ).first()

            phone_str = ''
            if phone:
                phone_str = f'({phone.code_area}) {phone.number[:5]}-{phone.number[5:]}'

            client_data = {
                'name': client.name,
                'phone': phone_str
            }

        # busca endereço do cliente
        from app.model.address import ModelAddress
        from app.model.client_address import ModelClientAddress
        client_address = ModelAddress.query.join(ModelClientAddress).filter(
            ModelClientAddress.client_id == session['client_id'],
            ModelAddress.status == StatusEnum.enabled
        ).first()

    return render_template('cart/checkout.html',
                           items=items,
                           total=total,
                           client_address=client_address,
                           form_data=client_data)


@SiteBlueprint.route('/cart/checkout', methods=['POST'])
def checkout_post():
    """Processa o pedido: salva na sessão e redireciona para login se necessário."""
    cart = get_cart()

    if not cart:
        return redirect(url_for('SiteBlueprint.cart_get'))

    data = request.form.to_dict()

    # ── Valida campos obrigatórios ──
    required = ['name', 'phone', 'delivery_date', 'delivery_time']
    errors = {}
    for field in required:
        if not data.get(field, '').strip():
            errors[field] = 'Campo obrigatório'

    if errors:
        items, total = _build_items(cart)
        return render_template('cart/checkout.html',
                               items=items, total=total,
                               errors=errors, form_data=data)

    # ── Salva dados do checkout na sessão para reaproveitar no signup/login ──
    session['checkout_data'] = data

    # ── Se não logado, redireciona para login ──
    if not session.get('client_id'):
        return redirect('/client/login?next=/cart/checkout/confirm')

    # ── Monta itens do carrinho ──
    items, total = _build_items(cart)

    if not items:
        return redirect(url_for('SiteBlueprint.cart_get'))

    # ── Salva no banco ──
    try:
        # 1. Cria o cliente
        model_client = ModelClient()
        client = model_client.create_client({'name': data['name']})
        if client is None:
            raise Exception('Erro ao criar cliente')

        # 2. Cria o pedido
        model_order = ModelOrder()
        order = model_order.create_order({'client_id': client.id})
        if order is None:
            raise Exception('Erro ao criar pedido')

        # 3. Cria os itens
        for item in items:
            model_item = ModelOrderItem()
            result = model_item.create_order_item({
                'order_id': order.id,
                'product_id': item['id'],
                'quantity': item['quantity']
            })
            if result is None:
                raise Exception(f'Erro ao salvar item {item["name"]}')

        # 4. Monta URL do WhatsApp
        msg = _build_whatsapp_message(data, items, total)
        whatsapp_url = f'https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={quote(msg)}'

        # 5. Salva na sessão e limpa carrinho
        session.pop('cart', None)
        session['pix_total'] = total
        session['pix_order_name'] = data['name']
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

    # ── Limpa carrinho após finalizar ──
    session.pop('cart', None)

    # ── Salva dados para a página PIX ──
    session['pix_total'] = total
    session['pix_order_name'] = data['name']
    session['pix_whatsapp_url'] = whatsapp_url

    # ── Monta mensagem do WhatsApp ──
    msg = _build_whatsapp_message(data, items, total)
    whatsapp_url = f'https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={quote(msg)}'

    # ── Redireciona pro PIX (que depois vai pro WhatsApp) ──
    return redirect(url_for('site_bp.pix_get', order_id=order.id))


# ── Confirmação após login ──

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

    items, total = _build_items(cart)
    if not items:
        return redirect(url_for('SiteBlueprint.cart_get'))

    try:
        model_order = ModelOrder()
        order = model_order.create_order({'client_id': session['client_id']})
        if order is None:
            raise Exception('Erro ao criar pedido')

        for item in items:
            model_item = ModelOrderItem()
            result = model_item.create_order_item({
                'order_id': order.id,
                'product_id': item['id'],
                'quantity': item['quantity']
            })
            if result is None:
                raise Exception(f'Erro ao salvar item {item["name"]}')

        msg = _build_whatsapp_message(data, items, total)
        whatsapp_url = f'https://api.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={quote(msg)}'

        session.pop('cart', None)
        session.pop('checkout_data', None)
        session['pix_total'] = total
        session['pix_order_name'] = data['name']
        session['pix_whatsapp_url'] = whatsapp_url

        return redirect(url_for('site_bp.pix_get', order_id=order.id))

    except Exception as e:
        LOGGER.exception(e)
        db.session.rollback()
        return redirect(url_for('SiteBlueprint.checkout_get'))


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
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'value': float(product.value),
                'path': product.path,
                'quantity': quantity,
                'subtotal': subtotal
            })
    return items, total


def _build_whatsapp_message(data, items, total):
    """Monta a mensagem formatada para o WhatsApp."""
    lines = []
    lines.append('🧺 *Novo Pedido - Amora Platter Box*')
    lines.append('')
    lines.append(f'👤 *Nome:* {data["name"]}')
    lines.append(f'📱 *Telefone:* {data["phone"]}')
    endereco = f'{data.get("street","")}, {data.get("street_number","")} {data.get("complement","")}'.strip(", ")
    endereco += f' — {data.get("district","")}, {data.get("city","")}/{data.get("state","")}, CEP {data.get("zip_code","")}'
    lines.append(f'📍 *Endereço:* {endereco}')
    lines.append(f'📅 *Data de entrega:* {data["delivery_date"]}')
    lines.append(f'🕐 *Horário:* {data["delivery_time"]}')

    if data.get('notes', '').strip():
        lines.append(f'📝 *Observações:* {data["notes"]}')

    lines.append('')
    lines.append('🛒 *Itens do Pedido:*')

    for item in items:
        lines.append(f'  • {item["name"]} × {item["quantity"]} — R$ {item["subtotal"]:.2f}')

    lines.append('')
    lines.append(f'💰 *Total: R$ {total:.2f}*')
    lines.append('')
    lines.append('_Pedido realizado pelo site Aurora Semijóias')

    return '\n'.join(lines)