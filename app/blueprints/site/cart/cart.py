# encoding: utf-8
from flask import render_template, make_response, request, jsonify, session, redirect, url_for
from app.blueprints.site import SiteBlueprint
from app import logging
from app.model.products import ModelProduct
from app.model.enum import StatusEnum

LOGGER = logging.getLogger(__name__)


def get_cart():
    """Retorna o carrinho atual da sessão."""
    return session.get('cart', {})


def save_cart(cart):
    """Salva o carrinho na sessão."""
    session['cart'] = cart
    session.modified = True


@SiteBlueprint.route('/cart', methods=['GET'])
def cart_get():
    """Exibe o carrinho de compras."""
    cart = get_cart()

    # Busca os dados completos dos produtos no carrinho
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

    return render_template(
        'cart/cart.html',
        items=items,
        total=total
    )


@SiteBlueprint.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    """Adiciona um produto ao carrinho."""
    product = ModelProduct.query.filter_by(
        id=product_id,
        status=StatusEnum.enabled
    ).first()

    if not product:
        return jsonify({'success': False, 'message': 'Produto não encontrado'}), 404

    cart = get_cart()
    key = str(product_id)

    quantity = int(request.form.get('quantity', 1))
    cart[key] = cart.get(key, 0) + quantity

    save_cart(cart)

    cart_count = sum(cart.values())

    return jsonify({
        'success': True,
        'message': f'"{product.name}" adicionado ao carrinho!',
        'cart_count': cart_count
    })


@SiteBlueprint.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    """Remove um produto do carrinho."""
    cart = get_cart()
    key = str(product_id)

    if key in cart:
        del cart[key]
        save_cart(cart)

    return redirect(url_for('SiteBlueprint.cart_get'))


@SiteBlueprint.route('/cart/update/<int:product_id>', methods=['POST'])
def cart_update(product_id):
    """Atualiza a quantidade de um produto no carrinho."""
    cart = get_cart()
    key = str(product_id)

    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    save_cart(cart)
    return redirect(url_for('SiteBlueprint.cart_get'))


@SiteBlueprint.route('/cart/clear', methods=['POST'])
def cart_clear():
    """Limpa todo o carrinho."""
    session.pop('cart', None)
    return redirect(url_for('SiteBlueprint.cart_get'))


@SiteBlueprint.route('/cart/count', methods=['GET'])
def cart_count():
    """Retorna a quantidade total de itens no carrinho (para o ícone da navbar)."""
    cart = get_cart()
    count = sum(cart.values())
    return jsonify({'count': count})