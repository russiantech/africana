from flask import jsonify, Blueprint, request
from flask_login import current_user, login_required

from web import db
from web.main.forms import ApportionForm

from web.models import Item, ApportionedItems, StockHistory
from web.utils.sequence_int import generator
from web.utils.db_session_management import db_session_management

apportion = Blueprint('apportion', __name__)

def exclude_deleted(query):
    return query.filter_by(deleted=False)

@apportion.route('/get_product_series', methods=['GET'])
def get_product_series():
    selected_department = request.args.get('dept')

    # Check if the selected department is valid
    if selected_department:
        # Query the database to get product series for the selected department
        product_series = Item.query.filter_by(dept=selected_department).with_entities(Item.id, Item.name).all()

        # Convert the result to a list of dictionaries with id and name
        product_series_data = [{'id': item[0], 'name': item[1]} for item in product_series]

        return jsonify(product_series_data)
    else:
        return jsonify([])  # Return an empty list if the department is not found


@apportion.route('/apportion', methods=['POST']) 
@login_required
@db_session_management
def apportion_():
    apportionform = ApportionForm()
    referrer =  request.headers.get('Referer') 
    
    #print(apportionform.data, apportionform.errors)
    
    if not apportionform.validate_on_submit(): #same-as-post-request
        print(f'{apportionform.errors}')
        #print(f'{apportionform.data}')
        return jsonify({ 
            'response': f'apportion-form-errors->{ apportionform.errors, apportionform.data}  </b>..',
            'flash':'alert-warning',
            'link': f'{referrer}'})
        
    if apportionform.validate_on_submit(): #same-as-post-request
        print(f"{apportionform.data}")

        """ qty = request.form.get('qty')
        item_ids = request.form.getlist('item_ids') """

        #item_series = apportionform.getlist('item_series')
        item_series = request.form.getlist('item_series')
        print(f"item-series->{item_series}")
        saved_portions = ApportionedItems(
            user_id = current_user.id if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
            items_qty = apportionform.item_qty.data,
            items_title = apportionform.item_title.data,
            #item_type = apportionform.item_type.data,
            #item_series=apportionform.item_series.data, 
            #item_dept=apportionform.item_dept.data if 'item_dept' in request.form else 'k', 
            deleted = False #This would ensure unique constraints defined under Item() model also works by excluding the deleted columns
            )

        for item_id in item_series:
            item = Item.query.get(item_id)
            #item = Item.query.get(int(item_id))
            if item:
                item.apportioned_quantities.append(saved_portions)

        db.session.add(saved_portions)
        db.session.commit()
        db.session.flush()
        db.session.refresh(saved_portions) #refresh so-i-can-get-the-last/new-insert-id

        #backup-stock-history when recording for the first time.
        saved_history = StockHistory(
            apportioned_item_id = saved_portions.id,
            apportioned_item = saved_portions, 
            user_id = saved_portions.user_id or current_user.id if current_user.is_authenticated else 0,
            version = generator.next(), #i created a func in utils.py to generate a sequencial int for me
            difference = saved_portions.items_qty,
            in_stock=saved_portions.items_qty, 
            #desc = f"{current_user.username} added <{saved_portions.qty}> of {saved_portions.name} on {saved_portions.updated}"
            desc = f"{current_user.username} added <{saved_portions.items_qty}> of some products on {saved_portions.updated}"
            )
        db.session.add(saved_history)
        db.session.commit()
        db.session.flush()
        db.session.refresh(saved_history) #refresh so-i-can-get-the-last/new-insert-id

        #print(f"{saved_portions}")

        return jsonify( { 
            'response': f'Success ..<b class="info"> {saved_portions.name}</b>.. Added!!',
            'flash':'alert-success',
            'link': f''})
    
    print('nothing come out ooooooooooooooooo')
    
