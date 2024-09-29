from flask import jsonify, Blueprint, request
from flask_login import current_user, login_required
from sqlalchemy import update
from web import db
from web.models import (
    Item, ApportionedItems, apportioned_items, StockHistory
)
from web.utils.sequence_int import generator
from web.utils.db_session_management import db_session_management
from web.main.forms import ApportionForm

apportion = Blueprint('apportion', __name__)

def exclude_deleted(query):
    return query.filter_by(deleted=False)

@apportion.route('/get_product_series', methods=['GET'])
def get_product_series():
    referrer =  request.headers.get('Referer') 
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

""" @apportion.route('/apportioned_items', methods=['GET'])
def get_apportioned_items():
    apportioned_items = ApportionedItems.query.all()
    # Convert the apportioned items to a JSON format and return it
    return jsonify([item.to_dict() for item in apportioned_items])
 """
#//create/apportinoning
@apportion.route('/apportion', methods=['POST']) 
@login_required
@db_session_management
def apportion_():
    referrer =  request.headers.get('Referer') 
    apportionform = ApportionForm()
    if not apportionform.validate_on_submit(): #same-as-post-request
        print(f'{apportionform.errors}')
        #print(f'{apportionform.data}')
        return jsonify({ 
            'response': f'apportion-form-errors->{ apportionform.errors}  </b>..',
            'flash':'alert-warning',
            'link': referrer})
        
    if apportionform.validate_on_submit(): #same-as-post-request
        #print(f"{apportionform.data}")
        items_series = request.form.getlist('items_series')
        #print(f"item-series->{items_series}")
        saved_portions = ApportionedItems(
            user_id = current_user.id if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
            items_dept = apportionform.items_dept.data,
            items_qty = apportionform.items_qty.data,
            items_title = apportionform.items_title.data,
            deleted = False #This would ensure unique constraints defined under Item() model also works by excluding the deleted columns
            )

        for item_id in items_series:
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
    
    print('nothing come out for invalid form ooooooooooo')
    
#//update 
@apportion.route('/apportion/<int:item_id>/update', methods=['PUT'])
@login_required
@db_session_management
def update_apportioned(item_id):
    referrer =  request.headers.get('Referer') 
    apportionform = ApportionForm()
    if apportionform.validate_on_submit():
        apportioned_item = ApportionedItems.query.get(item_id)

        # ...
        if apportioned_item:
            initial_apportioned_items_qty = apportioned_item.items_qty
           # Check if the user wants to update the items_qty
            if apportionform.items_qty.data is not None:
                try:
                    items_qty_eval = eval(apportionform.items_qty.data)
                    apportioned_item.items_qty = items_qty_eval
                except Exception as e:
                    return jsonify({
                        'response': f'Error evaluating items_qty: {str(e)}',
                        'flash': 'alert-danger',
                        'link': referrer
                    })

            # Check if the user wants to update the items_title
            if apportionform.items_title.data is not None:
                apportioned_item.items_title = apportionform.items_title.data

            items_series = request.form.getlist('items_series')
            #print(items_series)
            #if items_series is not None:
            if items_series and items_series is not None:  # Check if items_series is not an empty list
                # Clear the existing relationships, if new series to be related is provided
                apportioned_item.items.clear()

            for item_id in items_series:
                item = Item.query.get(item_id)
                if item:
                    apportioned_item.items.append(item)

            # Update the corresponding history backup
            stock_difference = int(initial_apportioned_items_qty - apportioned_item.items_qty) if (initial_apportioned_items_qty > apportioned_item.items_qty) \
                                            else int(apportioned_item.items_qty - initial_apportioned_items_qty)
            
            saved_history = StockHistory(
                    user_id=apportioned_item.user_id or current_user.id if current_user.is_authenticated else 0,
                    apportioned_item_id=apportioned_item.id,
                    apportioned_item=apportioned_item,
                    version=generator.next(),
                    difference=stock_difference,  # Negative value for reduction
                    in_stock=initial_apportioned_items_qty,
                    desc=f"{current_user.username} updated {apportioned_item.items_title} to <{apportioned_item.items_qty}> on {apportioned_item.updated}" 
                )
            
            """ history_entry = StockHistory.query.filter_by(apportioned_item_id=apportioned_item.id).first()
            if history_entry:  
                history_entry.difference = (initial_apportioned_items_qty - apportioned_item.items_qty) if initial_apportioned_items_qty > apportioned_item.items_qty \
                                else (apportioned_item.items_qty - initial_apportioned_items_qty)
                history_entry.in_stock = initial_apportioned_items_qty
                history_entry.desc = f"{current_user.username} updated {apportioned_item.items_title} to \
                    <{apportioned_item.items_qty}> on {apportioned_item.updated}"  # Remove the trailing comma
                history_entry.version = generator.next()

            db.session.add(apportioned_item) """

            db.session.add(saved_history)
            db.session.commit()
            db.session.flush()
            db.session.refresh(apportioned_item)

            return jsonify({
                'response': f'Success!. <b class="info"> {apportioned_item.items_title} </b> updated',
                'flash': 'alert-success',
                'link': referrer
            })

        return jsonify({
            'response': 'Apportioned item not found.',
            'flash': 'alert-warning',
            'link': referrer
        })
    
    return jsonify({
        'response': f'form invalidations->{apportionform.errors}',
        'flash': 'alert-warning',
        'link': referrer
    })

#//delete
@apportion.route('/apportion/<int:item_id>/delete', methods=['DELETE'])
def delete_apportioned(item_id):
    referrer =  request.headers.get('Referer') 
    apportioned_item = ApportionedItems.query.get(item_id)
    if not apportioned_item:
        return jsonify({
            'response': 'Apportioned item not found.',
            'flash': 'alert-warning',
            'link': referrer
        }), 404
    
    # Mark the apportioned item as deleted
    apportioned_item.mark_deleted()

    # Define the update statement
    update_statement = (
        update(apportioned_items)
        .where(apportioned_items.c.apportioned_id == apportioned_item.id)
        .values(deleted=True)
    )
    # Execute the update statement
    db.session.execute(update_statement)

    #//////////////////
    # Update
    """ post = Post.query.get(1)
    task = Task.query.get(1)
    post.tasks.append(task)
    db.session.commit()

    # Delete
    post = Post.query.get(1)
    task = Task.query.get(1)
    post.tasks.remove(task)
    db.session.commit()
    #////////////
    post = Post.query.get(1)
    task = Task.query.get(1)
    tasks_posts = db.Table('tasks_posts', db.metadata, autoload=True, autoload_with=db.engine)
    stmt = tasks_posts.delete().where(tasks_posts.c.post_id == post.id).where(tasks_posts.c.task_id == task.id)
    db.session.execute(stmt)
    db.session.commit() """
    #//////////////////////

    # Update the corresponding history
    history_entry = StockHistory.query.filter_by(apportioned_item_id=item_id).first()
    if history_entry:
        history_entry.in_stock -= apportioned_item.items_qty
        history_entry.deleted = True  # Optionally mark the history entry as deleted
        db.session.add(history_entry)
    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        'response': f'Successfully deleted <b class="info"> {apportioned_item.items_title}</b>.',
        'flash': 'alert-success',
        'link': referrer
    }), 200


