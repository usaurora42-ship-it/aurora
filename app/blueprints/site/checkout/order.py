# encoding: utf-8
from datetime import datetime
from flask import Flask, render_template, make_response, request, jsonify, session
from app.blueprints.site import SiteBlueprint

from app import logging
import json
from app.model.enum import StatusEnum
from app.model.order import ModelOrder
from app.model.order_item import ModelOrderItem
from app.model.session import ModelSession

LOGGER = logging.getLogger(__name__)

  
@SiteBlueprint.route('/cart/order', methods=['POST'])
def checkout_cart():
    data = request.form.to_dict() or {} 

    if 'user_id' not in session:
         return 'Login necessário', 403

    cart = json.loads(request.cookies.get('cart', '{}'))
    


    # query session
    query_session = ModelSession.query.with_entities(
         ModelSession.id
    ).filter_by(
        status=StatusEnum.enabled
    )

    # query order
    query_order = ModelOrder.query.with_entities(
        ModelOrder.id
    ).filter_by(
        status=StatusEnum.enabled
    )

    # query order itens
    query_order_item = ModelOrderItem.query.with_entities(
        ModelOrderItem.id
    ).filter_by(
        status=StatusEnum.enabled
    )
   

    #instance model session
    model_session = ModelSession()
    model_order = ModelOrder() 
    model_order_item = ModelOrderItem() 

    try:
         # create session
        #if session is None:

        session = query_session.first()
        session = ModelSession(user_id=session['user_id'], date_create=datetime.now())

        #
        # GET OR CREATE ORDER
        #
        order = query_order.first()
        order_item = query_order_item.first()

       
    # create order
        #if order is None:
        for product_id, quantity in cart.itens():
            data_order_item = {
                'product_id': data['product_id'],
                'quantity': data['quantity']
            }        
           
        
        order_item = model_order_item.create_order_item(data_order_item)

        # error to create order item
           
        if order_item is None:
            resp = make_response(render_template('orders/orders.html',
                        success=False,
                        errors=model_order_item.errors,
                        data_input=data))      
            resp.mimetype = 'text/html'
            return resp  
            
            
        # success response
        resp = make_response(render_template('orders/orders.html',                            
                                success=True,
                                errors=None))
        resp.mimetype = 'text/html'
        return resp
        

    except Exception as e:
            LOGGER.exception(e)
            resp = make_response(render_template('errors/500.html',                            
                                    success=False,
                                    errors=None))
            resp.mimetype = 'text/html'
            return resp, 500
    

