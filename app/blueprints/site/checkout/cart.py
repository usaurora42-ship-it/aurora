# encoding: utf-8
from flask import Flask, render_template, make_response, request, jsonify
from app.blueprints.site import SiteBlueprint

from app import logging
from app import environment
import json
from app.model.enum import StatusEnum
from app.model.cart import ModelCart
from app.model.cart_basket import ModelCartBasket
from app.model.products import ModelProduct


LOGGER = logging.getLogger(__name__)

# def breakfast_baskets_get():    
#     # query breakfast baskets    
#     query_breakfast = ModelBasket.query.with_entities(
#         ModelBasket.description,
#         ModelBasket.path,
#         ModelBasket.value
#     ).filter_by(
#         status=StatusEnum.enabled,
#         category_id=5
#     ).order_by(ModelBasket.description)

#     breakfast_baskets = query_breakfast.all()

#     return breakfast_baskets

# @SiteBlueprint.route('/baskets/breakfast_details', methods=['POST'])
# def breakfast_details_post():    
#     data = request.form.to_dict() or {} 

    
@SiteBlueprint.route('/cart/cart')
def cart_get():
    cart_cookie = request.cookies.get('cart')
    if not cart_cookie:
         return jsonify({'mensagem': 'Carrinho vazio', 'itens':[]})
    
    cart = json.loads(cart_cookie)
    products_ids = list(map(int, cart.keys()))
    products = ModelProduct.query.filter(ModelProduct.id.in_(products_ids)).all()

    itens = []
    for product in products:
         itens.append({
              'id': product.id,
              'name': product.name,
              'value': product.value,
              'quantity': cart[str(product.id)],
              'subtotal': cart[str(product.id)] * product.value
         })    

    return jsonify(itens)
    
    # resp = make_response(render_template('cart/cart.html',
    #     success=False,
    #     errors=None,
    #     data_input=None))
    # resp.mimetype = 'text/html'
    # return resp 

@SiteBlueprint.route('/cart/cart', methods=['POST'])
def cart_post(cart_uuid):  
    data = request.form.to_dict() or {}    

    # query cart
    query_cart = ModelCart.query.with_entities(
        ModelCart.id    
    ).filter_by(
        status=StatusEnum.enabled,
        uuid = cart_uuid
    )

    print("uuid_cart ")
    print(cart_uuid)
    # instance models
    model_cart = ModelCart()  
    
    
    try:       
        
        #
        # GET OR CREATE CART
        #
        cart = query_cart.first()
        print("cart")
        print(cart)
        
    # create cart
        if cart is None:
            data_cart = {
                'amount': data['qtdBasket'],
                'value': data['value_basket'],            
                'total': float(data['qtdBasket']) * float(data['value_basket'])
            }   
            cart = model_cart.create_cart(data_cart)
        else:
            data_cart = {
                'amount': data['qtdBasket'],
                'value': data['value_basket'],            
                'total': float(data['qtdBasket']) * float(data['value_basket'])
            }   
            print("entrei aqui agora")
            print(data_cart)
            cart = model_cart.update_cart(data_cart)

        # errors
        if cart is None:
            resp = make_response(render_template('cart/cart.html',
                        success=False,
                        errors=model_cart.errors,
                        data_input=data))
            resp.mimetype = 'text/html'
            return resp 

        id_basket = request.values.get("id_basket")

        model_cart_basket = ModelCartBasket()


        data_cart_basket = {
            'basket_id': id_basket,
            'cart_id': cart.id
        }
        

        cart_basket = model_cart_basket.create_cart_basket(data_cart_basket)
        

        # error to create cart basket           
        if cart_basket is None:
            resp = make_response(render_template('cart/cart.html',
                        success=False,
                        errors=model_cart_basket.errors,
                        data_input=data))      
            resp.mimetype = 'text/html'
            return resp  
        
        # basket_products = query_basket.filter(
        #             ModelBasket.id == basket.id,
        #             ModelProduct.id == products.id
        #         ).first()

        # product = request.values.getlist("product")

        # for p in product:

        #     model_basket_product = ModelBasketProduct()


        #     data_basket_product = {
        #         'basket_id': basket.id,
        #         'product_id': p
        #     }

        #     basket_product = model_basket_product.create_basket_product(data_basket_product)

        # # error to create basket           
        # if basket_product is None:
        #     resp = make_response(render_template('baskets/breakfast.html',
        #                 success=False,
        #                 errors=model_basket.errors,
        #                 data_input=data))      
        #     resp.mimetype = 'text/html'
        #     return resp  
            
        # success response
        resp = make_response(render_template('cart/cart.html',                            
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
