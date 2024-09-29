#from sqlite3 import IntegrityError
#from sqlalchemy import exc
#from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc


from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import current_user
from web import db
from web.models import Item, Order
from web.cart.forms import OrderForm, OrderForm

cart = Blueprint('cart', __name__)

def payOptionCheck(option, amt=500):
    
    try:
        if option == 'fw':
            return redirect(url_for('pay.payform', amt=amt))
        
        elif option ==  'ps':
            return redirect(url_for('pay.payform', amt=amt))
        
        elif option ==  'pp':
            return redirect(url_for('pay.payform', amt=amt))
        
        elif option ==  'cash' | 'chq':
            pass
        elif option ==  None:
            return redirect(url_for('pay.payform', amt=amt))
        else:
            flash(f'Amount Or Cart Is Missing', category='danger')
            #return f"Amount Or Cart Is Missing"
            pass
    except Exception as e:

        flash(f'Error Occured {e}', category='info')
        return f"{e}"
    
def which_option(option):
    try:
        if option ==  'fw':
            return 'Flutterwaves'
        
        elif option ==  'ps':
            return 'Paystack'
        
        elif option ==  'pp':
            return 'Paypal'
        
        elif option ==  'cash' | 'chq':
            return 'Cash/Cheque payment'
        if option == None:
            return 'Cash on delivery'
        else:
            flash(f'payment option missing', category='danger')
            return f"payment option missing"
    
    except Exception as e:

        flash(f'Error Occured {e}', category='success')
        return f"{e}"
    
#<action> -> save/remove/update/wipe/_
@cart.route('/basket/<action>', methods=['GET','POST'])
def basket(action):

    action, item, qty = str(action) , str(request.args.get('item')), int(request.args.get('qty', 1 ))
    
    cart = session.get('basket', {})

    try:

            if action ==  'save':

                if Item.item_exists(item):
                    cart[item] = (cart.get(item, 0) + qty)
                    session['basket'] = cart
    
                    return 'Success, You\'ve Added To Your Shopping Basket'
                return 'Failed!, This Item Is Not Found'
            
            elif action ==  'update':
                if item in cart and qty is not None:
                    cart[item] = qty
                    session['basket'] = cart
                    return 'Success, You\'ve Updated Your Cart'
                #if not carted-already, but want-to update, save as new item in cart, with value to be updated with
                elif Item.item_exists(item):
                    cart[item] = (cart.get(item, 0) + qty)
                    session['basket'] = cart
                    return 'Success, You\'ve Updated Your Cart'
                
                return 'Failed, Unable To Update Your Shopping Cart'
            
            elif action ==  'remove':
                if item in cart:
                    del cart[item]
                    session['basket'] = cart
                    
                    return 'Success, You\'ve Removed From Your Cart'
                return 'Sorry, Unable To Remove From Your Shopping Cart'
            
            elif action ==  'wipe':
                if len(cart) > 0 :
                    del session['basket']

                    return 'Success, You\'ve Emptied Your Cart'
                return 'Sorry, Unable To Wipe-Off Your Shopping Cart'
            
            elif action == 'cart_items':
                if len(cart) > 0 :
                    return cart
                return 'Sorry, Your Cart Is Empty'
                    
            else :

                if len(cart) > 0 :

                    carted = Item.query.filter(Item.id.in_(cart.keys())).all()

                    sub_total =  sum([c.price * int(cart[str(c.id)]) for c in carted ]) 

                    item_count = len(carted) #from-db-count

                    baskt = [{ 
                            'item': c.id, 
                            'name': c.name, 
                            'photo': c.photos[0], 
                            'qty':  cart.values() if c.id in cart.keys() else 1 ,
                            'qty':  cart[str(c.id)] ,
                            'price':  c.price, 
                            'total_each':  c.price * int(cart[str(c.id)]) ,
                            'attr': c.attributes[0],
                        } for c in carted] , sub_total, item_count
                    
                    #session['basket'] = cart
                    return jsonify(baskt)
            session.modified = True
            return jsonify(cart)

    except Exception as e:

        return jsonify(e)
   
#<int:o_id> == <int:order_id
@cart.route("/ordered/<int:o_id>", methods=['GET', 'POST'])
def ordered(o_id):

    try:

        order = Order.query.filter( Order.order_id == o_id ).first_or_404()

        dt = order.order_item

        items = Item.query.filter(Item.id.in_(dt.keys() )).all()

        sub_total =  sum([i.price * int(dt[str(i.id)]) for i in items ]) 

        item_count = len(items) #from-db-count

        #LEAVE THIS CONTEXT, IN CASE YOU NEED TO USE A JSON ENDPOINT
        """ context = [{ 
                'item': i.id, 
                'name': i.name, 
                'photo': i.photos[0], 
                'qty':  dt[str(i.id)] ,
                'price':  i.price, 
                'total_each':  i.price * int(dt[str(i.id)]) ,
                'attr': i.attributes[0],
            } for i in items] , sub_total, item_count 
        #return f"{context}" 
        #return f"{[item.name for item in items]}"
        
        """

        context = {

            'order_id': order.order_id,
            'order_name': order.name,
            'order_email': order.email,
            'order_phone': order.phone,
            'order_country': order.country,
            'order_state': order.state,
            'order_adrs': order.adrs,
            'order_zipcode': order.zipcode,
            'order_status': order.order_status,

            'order_payment_option':  which_option(order.pment_option), 
            'order_created': order.created,

            'sub_total': sub_total,
            'item_count': item_count,

            'order_item': [{ 
                'item': i.id, 
                'name': i.name, 
                'photo': i.photos[0], 
                'qty':  dt[str(i.id)],
                'price':  i.price, 
                'total_each':  i.price * int(dt[str(i.id)]),
                'attr': i.attributes[0],
            } for i in items ]
        }

    except Exception as e:
        return f"{e}"
    
    return render_template('invoice.html', **context )


""" class ExampleException(Exception):
    def __init__(self, foo):
        self.foo = foo
        try:
            raise ExampleException("Bar!")
        except ExampleException as e:
            print e.foo """

""" class CustomIntegrity(exc.IntegrityError):
    def __init__(self, orderd_id):
        self.orderd_id = orderd_id
        
        try:
            raise CustomException("Bar!")
        except CustomException as e:
            print e.ordered_id """

#create order
""" 
class CustomIntegrity(exc.IntegrityError):
    def __init__(self, oid):
        self.oid = oid
        #return redirect(url_for('cart.ordered', o_id=orderd_id)) """


""" from weasyprint import HTML

def htmlpdf(html_url):
    HTML(html_url).write_pdf( html_url + '.pdf' ) """

@cart.route('/basket', methods=['GET','POST'])
def baskt():
    form = OrderForm()
    cart = session.get('basket', {})

    #order_id = random.randint(0, 999999) #this-one-changes-often, so not suitable, there's a default one generated @ db level
    
    try:
        if form.validate_on_submit():

            ordered = Order( 
                
                usr_id = current_user.id \
                    if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
                
                order_item = cart, #bcos from up, if no carted-item, it won't run

                #order_id=order_id, 

                email=form.email.data, 
                phone=form.phone.data,
                name=form.name.data, 
                adrs=form.adrs.data, 
                country=form.country.data, 
                state=form.state.data, 
                zipcode=form.zipcode.data, 
                #ordert_amt=form.ordert_amt.data, 
                pment_option=form.pment_option.data, 

                )

            db.session.add(ordered)
            db.session.commit()
            db.session.flush()
            
            db.session.refresh(ordered) #refresh so-i-can-get-the-last/new-insert-id

            pay = payment_option( form.pment_option.data, amt=int(float(form.ordert_amt.data)) )

            session['recent_order'] = ordered.order_id #save-order-id in session so it can be retrieved from exception block incase or of IntegrityError

            if len(session['basket']) > 0 :
                del session['basket']  #remove it from cart if saved to db as order
            return pay if pay and ordered.order_id else redirect(url_for('cart.ordered', o_id=ordered.order_id)) 
        
    except exc.IntegrityError as e:
            print(e)
            db.session.rollback()
            #cart = session.get('recent_order', {})
            flash(f"Success !!!, You're Order Was Placed ", "info")
            return redirect(url_for('cart.ordered', o_id=session.get('recent_order', 0))) 
            #return f"Order Already Placed Successfully {session['recent_order']}"
    
    except Exception as e:
            print(e)
            db.session.rollback()
            flash(f"Oops an error occured, pls try again-> ", "info")
            return f"\n Error!!! Kindly Try Again"

    return render_template('basket.html', cart=cart, form=form)



@cart.route("/order", methods=['GET', 'POST'])
def order():
    form = OrderForm() 
    """if request.method == "POST":
        flash(form.data, 'warning')""" 
    try:
        if form.validate_on_submit():
            order_info = Order( 
                usr = current_user.id if current_user.is_authenticated else None, #so that even-if you're not logged in, you can still place orders
                email=form.email.data, 
                phone=form.phone.data,
                name=form.name.data, 
                state=form.state.data, 
                bustop=form.bustop.data, 
                street=form.street.data, 
                )

            db.session.add(order_info)
            db.session.commit()
            flash('Order Details Recorded !', category='success')
            #return redirect(request.referrer)
            return "Order Details Recorded !"
    except Exception as e:
        return f"{e}"
    
    return render_template('checkout.html', form=form)