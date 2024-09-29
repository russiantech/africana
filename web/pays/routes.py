import json
import os, requests, string , random
from flask_login import current_user
from flask import flash, redirect, render_template, request, Blueprint, url_for
from web.pays.forms import PayForm, OrderInfoForm
from web.models import Order 
from web import db
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
print(load_dotenv(find_dotenv()))
pay = Blueprint('pay', __name__)

sk = os.environ.get('RAVE_SECRET_KEY')
pk = os.environ.get('FW_PUBK') 
#pk = 'FLWPUBK_TEST-cdc9d0403781231185467d049802ff48-X' 
tx_ref = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))

@pay.route("/pay/<int:amt>",  methods=['GET', 'POST'])
def payform(amt):
    form = PayForm()
    form.email.data = current_user.email if current_user.is_authenticated else form.email.data #update-email-from-logged-in user before submitting
    form.amt.data = amt #update-amt-from-url before submitting
    context = {'form':form, 'amt': amt }

    return render_template('payform.html', **context )

""" docs..1.send amt to " /pay/<amount>" 2. collect amount, update the email form, and post both amt & email to "/pay" """
@pay.route("/pay", methods=['GET', 'POST'])
def initiate():
    if request.method == "GET":
        #return redirect(request.referrer)
        pass
    try:
        """This is used to initiate standard payments. It takes in the arguments and returns the url to redirect users for payments """
        verify_pay = f"{request.url_root + url_for('pay.verify')}"
        logo_url = f"{request.url_root + url_for('static', filename='img/logo/affordable1.png')}"
        payment_url = "https://api.flutterwave.com/v3/payments"
        #user
        amt = request.form.get('amt')
        email = request.form.get('email')
        payload = json.dumps({
            "tx_ref": f"{tx_ref}",
            "amount": f"{amt}",
            "currency": f"NGN".upper(),
            "redirect_url": f"{verify_pay}",
            "payment_options": "card,  ussd, account",
            "customer": {
                "email": f"{email}",
            },
            "customizations": {
                "title": "Quality Generators",
                "description": "Payment For Generator(s)",
                "logo": f"{logo_url}"
            }
        })
        headers = {
            'Authorization': f'Bearer {sk}',
            'Content-Type': 'application/json'
        }

        response = requests.post(payment_url,headers=headers, data=payload)
        link = response.json()["data"]["link"]
        flash('Weldone!!! Proceed Here', 'success')
        return redirect(link)
        
    except Exception as e:
        flash(f'error !!!, {e}', 'danger')
        print(f'error!!!, {e}')
        return f"error!!!, {e}"

@pay.route("/verify")
def verify():
    verify_enpoint = f"https://api.flutterwave.com/v3/transactions/{request.args.get('transaction_id')}/verify"
    pass

@pay.route("/deliver-to", methods=['GET', 'POST'])
def order_info():
    form = OrderInfoForm() 
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