from flask import jsonify, Blueprint, request
from flask_login import current_user, login_required

from web import db
from web.main.forms import ApportionForm

from web.models import Item, ApportionedItems, apportioned_items, StockHistory
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

@apportion.route('/apportioned_items', methods=['GET'])
def get_apportioned_items():
    apportioned_items = ApportionedItems.query.all()
    # Convert the apportioned items to a JSON format and return it
    return jsonify([item.to_dict() for item in apportioned_items])

#//create/apportinoning
@apportion.route('/apportion', methods=['POST']) 
@login_required
@db_session_management
def apportion_():
    apportionform = ApportionForm()
    referrer =  request.headers.get('Referer') 

    if not apportionform.validate_on_submit(): #same-as-post-request
        print(f'{apportionform.errors}')
        #print(f'{apportionform.data}')
        return jsonify({ 
            'response': f'apportion-form-errors->{ apportionform.errors}  </b>..',
            'flash':'alert-warning',
            'link': referrer})
        
    if apportionform.validate_on_submit(): #same-as-post-request
        #print(f"{apportionform.data}")
        item_series = request.form.getlist('item_series')
        #print(f"item-series->{item_series}")
        saved_portions = ApportionedItems(
            user_id = current_user.id if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
            items_dept = apportionform.item_dept.data,
            items_qty = apportionform.item_qty.data,
            items_title = apportionform.item_title.data,
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
            desc = f"{current_user.username} added <{saved_portions.items_qty}> for some products({saved_portions.items_title}) on {saved_portions.updated}"
            )
        db.session.add(saved_history)
        db.session.commit()
        db.session.flush()
        db.session.refresh(saved_history) #refresh so-i-can-get-the-last/new-insert-id
        
        return jsonify( { 
            'response': f'Success ..<b class="info"> {saved_portions.items_title}</b>.. Added!!',
            'flash':'alert-success',
            'link': referrer})
    
    print('nothing come out ooooooooooooooooo')
    
#//update 
@apportion.route('/apportion/<int:item_id>/update', methods=['PUT'])
@login_required
@db_session_management
def update_apportioned(item_id):
    apportionform = ApportionForm()
    if apportionform.validate_on_submit():
        apportioned_item = ApportionedItems.query.get(item_id)

        if apportioned_item:
            # Update ApportionedItem attributes
            apportioned_item.items_qty = apportionform.item_qty.data
            apportioned_item.items_title = apportionform.item_title.data

            # Update the many-to-many relationship with items
            item_series = request.form.getlist('item_series')
            apportioned_item.apportioned_quantities = []  # Clear existing relationships

            for item_id in item_series:
                item = Item.query.get(item_id)
                if item:
                    apportioned_item.apportioned_quantities.append(item)

            # Update the corresponding history backup
            history_entry = StockHistory.query.filter_by(apportioned_item_id=apportioned_item.id).first()
            if history_entry:
                history_entry.difference = apportioned_item.items_qty
                history_entry.in_stock = apportioned_item.items_qty
                history_entry.desc = f"{current_user.username} updated <{apportioned_item.items_qty}> for some products ({apportioned_item.items_title}) on {apportioned_item.updated}"

            db.session.add(apportioned_item)
            db.session.commit()
            db.session.flush()
            db.session.refresh(apportioned_item)

            return jsonify({
                'response': f'Successfully updated <b class="info">{apportioned_item.items_title}</b>.',
                'flash': 'alert-success',
                'link': f''
            })
        else:
            return jsonify({
                'response': 'Apportioned item not found.',
                'flash': 'alert-warning',
                'link': f''
            })
    else:
        return jsonify({
            'response': 'Invalid form data. Please check your input.',
            'flash': 'alert-warning',
            'link': f''
        })

#//delete
@apportion.route('/apportion/<int:item_id>/delete', methods=['DELETE'])
def delete_apportioned(item_id):
    apportioned_item = ApportionedItems.query.get(item_id)
    if not apportioned_item:
        return jsonify({
            'response': 'Apportioned item not found.',
            'flash': 'alert-warning',
            'link': f''
        }), 404
    
    # Mark the apportioned item as deleted
    apportioned_item.mark_deleted()

    # Query the apportioned_items table to get the associations
    """ associations = apportioned_items.query.filter_by(apportioned_id=apportioned_item.id).all()
    for association in associations:
        # Modify the 'deleted' flag for the association
        association.deleted = True
        db.session.add(association) """
    
    from sqlalchemy import update

    # Define the update statement
    update_statement = (
        update(apportioned_items)
        .where(apportioned_items.c.apportioned_id == apportioned_item.id)
        .values(deleted=True)
    )

    # Execute the update statement
    db.session.execute(update_statement)
    #db.session.commit()

    """ #associations = db.session.query(apportioned_items).filter(apportioned_items.c.apportioned_id == apportioned_item.id).all()
    associations = db.session.query(apportioned_items).filter(apportioned_items.c.apportioned_id == apportioned_item.id).all()
    # Update the 'deleted' flag for the retrieved associations
    for association in associations:
        #association.deleted = True
        #association.update().values(deleted=True)
        association.update(deleted=True)
        pass """

    """ from sqlalchemy import select
    #stmt = apportioned_items.update().where(apportioned_items.c.apportioned_id == apportioned_item.id).values(deleted=True)
    stmt = apportioned_items.update().where(apportioned_items.c.apportioned_id == apportioned_item.id).values(deleted=True)
    if apportioned_item:
        # Build a SQL expression to update the 'deleted' flag
        #stmt = apportioned_items.update().where(apportioned_items.c.apportioned_id == apportioned_item.id).values(deleted=True)
        # Execute the SQL statement
        db.session.execute(stmt) """

    """ for association in apportioned_item.items:
        # Set the 'deleted' flag to True for the item association
        association.deleted = True
        db.session.add(association) """
    
    # Update the corresponding history
    history_entry = StockHistory.query.filter_by(apportioned_item_id=item_id).first()
    if history_entry:
        history_entry.in_stock -= apportioned_item.items_qty
        history_entry.deleted = True  # Optionally mark the history entry as deleted
        db.session.add(history_entry)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        'response': f'Successfully deleted <b class="info">{apportioned_item.items_title}</b>.',
        'flash': 'alert-success',
        'link': f''
    }), 200


