# encoding: utf-8
from flask import render_template, request, session, redirect, url_for
from app.blueprints.site import SiteBlueprint
from app import logging
from app.lib.pix import gerar_pix

LOGGER = logging.getLogger(__name__)


@SiteBlueprint.route('/cart/pix/<int:order_id>', methods=['GET'])
def pix_get(order_id):
    """Exibe a página de pagamento PIX com QR Code."""

    # Recupera o total salvo na sessão após o checkout
    total = session.get('pix_total', 0.0)
    order_name = session.get('pix_order_name', 'Pedido')

    if not total:
        return redirect(url_for('SiteBlueprint.cart_get'))

    # Gera o PIX
    pix = gerar_pix(
        valor=total,
        txid=str(order_id),
        descricao='Amora Platter Box'
    )

    return render_template(
        'cart/pix.html',
        pix=pix,
        order_id=order_id,
        order_name=order_name,
        whatsapp_url=session.get('pix_whatsapp_url', '/')
    )
