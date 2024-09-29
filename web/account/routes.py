from flask import redirect, render_template, stream_template, jsonify, Blueprint, url_for, flash, session, request
from flask_login import current_user
from sqlalchemy import exc
from web import db
from web.utils.ip_adrs import user_ip
from web.models import User, Cate, Order, Item, Tag
from web.account.forms import OrderForm, PostForm

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
    
acct = Blueprint('acct', __name__)

@acct.route('/posts', methods=['POST', 'GET']) 
@acct.route('/<iid>/posts', methods=['POST', 'GET']) 
def save_listing(iid=None):
    form = PostForm()
    try:
        
        if form.validate_on_submit(): #same-as-post-request
            
            it = Item.query.filter(Item.id == iid).first()
            c = Cate.query.filter_by(name=form.cate.data).first() or Cate(name=form.cate.data)
            #owner = User.query.filter(User.id== ( ( current_user.id if current_user.is_authenticated else form.usr.data) or None ) ).first()
            t = Tag.query.filter_by(Tag.name==form.tag.data|Tag.name.in_(form.tag.data)|Tag.name.like(form.tag.data) ).first() or Tag(name=form.tag.data)
            
            #save-new-listing
            if request.method == 'POST' and not it: 
                listing = Item( 
                owner = current_user if current_user.is_authenticated else 0,
                name = form.title.data,
                price = form.price.data,
                disc = form.disc.data,
                desc = form.desc.data,
                photos =  form.photo.fee.data, #[]
                color = form.color.data, #[]
                quant = form.quant.data,
                attributes = form.attributes.data, #[]
                size = form.size.data, #[]
                ip = user_ip(),
                cate = [c], #[]
                tag = [t], #[list/array-of tag ids the prdct belongs to/can be tagged-with]
                )

            db.session.add(listing)
            db.session.commit()
            db.session.flush()
            db.session.refresh(listing) #refresh so-i-can-get-the-last/new-insert-id
            
            #making updates/iid(item-id)
            if request.method == 'POST' and it:
                it.owner = current_user if current_user.is_authenticated else 0
                it.name = form.title.data
                it.price = form.price.data
                it.disc = form.disc.data
                it.desc = form.desc.data
                it.photos =  form.photo.fee.data #[]
                it.color = form.color.data#[]
                it.quant = form.quant.data
                it.attributes = form.attributes.data#[]
                it.size = form.size.data#[]
                it.ip = user_ip()
                it.cate = [c] #[]
                it.tag = [t] #[list/array-of tag ids the prdct belongs to/can be tagged-with]
                db.session.commit()
                flash(f'Success {form.title.data} updated!', 'success')
                return jsonify( { 
                    'response': f'Success {form.title.data} updated!',
                    'flash':'alert-success',
                    'link': f'{url_for("acct.me")}'})
            
        #read/view-only
        elif request.method == 'GET' and it is not None:
            form.owner.data = it.owner
            form.name.data = it.name
            form.price.data = it.lang
            form.desc.data = it.desc
            form.disc.data = it.disc
            form.photo.data = [x for x in it.photo]
            form.color.data = [x for x in it.color]
            form.quant.data = it.quant 
            form.attributes.data = [x for x in it.attributes]
            form.size.data =  [x for x in it.size] #[]
            #form.ip.data = it.ip
            form.cate.data = [x for x in it.cate ]
            form.tag.data = [x for x in it.tag]#[list/array-of tag ids the prdct belongs to/can be tagged-with]

            return jsonify( { 
                'response': f'warning!!!, Invalid Request',
                'flash':'alert-danger',
                'link': f'#'})
        
    except exc.IntegrityError as e:
        print(e)       
        db.session.rollback()
        return jsonify( 
            { 
            'response': f'Item listed already, click below to preview',
            'flash':'alert-primary',
            'link': f'{ url_for("main.index")}'
            })
    
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(f"Oops an error occured, pls try again-> ", "primary")
        return jsonify( { 
            'response': f'ooops!!!, Error occured, kindly try again({e})',
            'flash':'alert-primary' })
    

@acct.route('/ordering', methods=['POST', 'GET']) # -> basket, merged with checkout in same route
def save_order():
    
    form = OrderForm()

    form.order_amt.data = 500

    cart = session.get('basket', {})
    
    try:

        if len(cart) < 1 :
            return jsonify( { 
                'response': f'Your Shopping Basket Is Empty, Browse Salesnet & Add Item(s) To Contine',
                'flash':'alert-primary',
                'link': f'{url_for("main.index")}',
                #'receipt': f'{url_for("cart.ordered", o_id=session["recent_order"])}'
                             })
        
        if form.validate_on_submit():

            ordered = Order( 
                
                usr_id = current_user.id \
                    if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
                
                order_item = cart, #bcos from up, if no carted-item, it won't run

                email=form.email.data, 
                phone=form.phone.data,
                name=form.name.data, 
                adrs=form.adrs.data, 
                country=form.country.data, 
                state=form.state.data, 
                zipcode=form.zipcode.data, 
                #order_amt=form.order_amt.data, 
                pment_option=form.pment_option.data, 

                )

            db.session.add(ordered)
            db.session.commit()
            db.session.flush()
            
            db.session.refresh(ordered) #refresh so-i-can-get-the-last/new-insert-id

            pay = payOptionCheck( form.pment_option.data, amt=int(float(form.order_amt.data)) )

            session['recent_order'] = ordered.order_id #save-order-id in session so it can be retrieved from exception block incase or of IntegrityError
            session['pay_link'] = pay #save-payment-link in session so it can be retrieved from exception block incase for the front-end

            #if len(session['basket']) > 0 :
            del session['basket']  #remove it from cart if saved to db as order
            
            #return pay if pay and ordered.order_id else redirect(url_for('cart.ordered', o_id=ordered.order_id)) 

            if pay and ordered.order_id:
                return jsonify( { 
                'response': f'Success!!!, Your Order Was Placed, Contine To {which_option(ordered.pment_option)} ',
                'flash':'alert-success',
                'link': f'{pay}',
                 'receipt': f'{url_for("cart.ordered", o_id=ordered.order_id)}' })
            
        flash(f'{form.errors}', 'info')
        return jsonify( { 
                'response': f'{form.errors}',
                'flash':'alert-primary'
                             }) 
        
    except exc.IntegrityError as e:
            print(e)
            recent_order = session.get("recent_order", False )
            pay_link = session.get("pay_link", False )
                                  
            db.session.rollback()
            return jsonify( { 
                'response': f'This order (#{ recent_order }) has been recorded already,\
                proceed to making payments/geting receipt',
                'flash':'alert-primary',
                'link': f'{ pay_link or url_for("cart.ordered", o_id=recent_order)   }',
                'receipt': f'{url_for("cart.ordered", o_id=recent_order )}'
                             })
    
    except Exception as e:
            print(e)
            db.session.rollback()
            flash(f"Oops an error occured, pls try again-> ", "primary")
            return jsonify( { 
                'response': f'ooops!!!, an error occured, kindly try again({e})',
                'flash':'alert-primary' })
    
@acct.route("/<usr>/account")
@acct.route("/account")
def me(usr=None):
    context = {
        'pname' : 'Account'
    }
    return render_template('account/me3.html')

@acct.route('/browsed')
def history():
    context = {
        'pname' : 'History'
    }
    return render_template("account/history.html", **context)

@acct.route('/<item>/saved')
@acct.route('/saved')
def saved(item=None):
    context = {'pname' : 'Favorite'}
    return render_template("account/saved.html", **context)

@acct.route('/cart', methods=['POST', 'GET']) # -> basket, merged with checkout in same route
def cart():

    form = OrderForm()

    form.order_amt.data = 500

    context = { 'pname' : 'Basket', 'form' : form }

    return render_template("account/cart2.html", **context)

@acct.route('/track')
def track():
    context = {
        'pname' : 'Tracking'
    }
    return render_template("account/track.html", **context)

@acct.route('/invoice')
def invoice():
    context = {
        'pname' : 'Invoice'
    }
    return render_template("account/invoice.html", **context)

@acct.route('/followed')
def followed():
    context = {
        'pname' : 'Followed'
    }
    return render_template("account/followed.html", **context)

@acct.route('/chat')
def chat():
    context = {
        'pname' : 'Chats'
    }
    return render_template("account/checkout.html", **context)


####### VENDORS ######################
@acct.route('/post', methods=['GET', 'POST'])
def post():

    form = PostForm()
    cate = Cate.query.order_by(Cate.id).all()
    cate = [ {'id': c.id, 'parent': c.parent, 'name': c.name, 'lev':c.lev } for c in cate ]
    context = { 'pname' : 'listing', 'form': form, 'cate': cate,  }
    
    return stream_template("account/post.html", **context)

@acct.route("/<usr>/vendor")
@acct.route('/vendor')
def vendor(usr=None):
    context = {
        'pname' : 'Vendor'
    }
    return render_template("account/vendor.html", **context)

@acct.route("/<usr>/shop")
@acct.route('/shop')
def shop(usr=None):
    context = {
        'pname' : 'Neon Shops'
    }
    return render_template("account/shop.html", **context)

@acct.route("/<usr>/brands")
@acct.route('/brands')
def brand(usr=None):
    context = {
        'pname' : 'Brands'
    }
    return render_template("account/brand.html", **context)








