from flask import jsonify, Blueprint, request, url_for, flash
from flask_login import current_user, login_required

from datetime import datetime
from random import randint
from sqlalchemy import and_
from sqlalchemy.sql import func

from sqlalchemy import and_
from sqlalchemy.sql import func

from web import db
from web.models import (
    Items, Apportion, StockHistory,
    Expenses, Items, Apportion, StockHistory, Sales
)
from web.utils.sequence_int import generator
from web.utils.db_session_management import db_session_management
from web.main.forms import ApportionForm
from web.main.forms import SalesForm, RangeForm

from web.utils.ip_adrs import user_ip

bar = Blueprint('bar', __name__)

def exclude_deleted(query):
    return query.filter_by(deleted=False)

@bar.route('/get_product_series', methods=['GET'])
def get_product_series():
    referrer =  request.headers.get('Referer') 
    selected_department = request.args.get('dept')

    # Check if the selected department is valid
    if selected_department:
        # Query the database to get product series for the selected department
        product_series = Items.query.filter_by(dept=selected_department).with_entities(Items.id, Items.name).all()

        # Convert the result to a list of dictionaries with id and name
        product_series_data = [{'id': item[0], 'name': item[1]} for item in product_series]

        return jsonify(product_series_data)
    else:
        return jsonify([])  # Return an empty list if the department is not found

#//create/apportinoning
@bar.route('/s_range/sales', methods=['POST']) 
@login_required
@db_session_management
def s_range():
    rangeform = RangeForm()
    if rangeform.validate_on_submit() and ("start" or "end") in request.form: #same-as-post-request\
        def get_expenses(start, end, dept):
            # Swap dates if end_date is less than start
            if end < start:
                start, end = end, start
            xp = Expenses.query.filter(and_(func.date(Expenses.created) == start, Expenses.dept == dept)  if start == end else \
            and_(Expenses.created >= start, Expenses.created <= end, Expenses.dept == dept), Expenses.deleted == False ).all()
            #xp = Expenses.query.filter( and_(Expenses.created >= start, Expenses.created <= end, Expenses.dept == dept ) ).all()
            return xp

        # Function to query sales within the date range func.max(Sale.date))
        def get_sales(start, end, dept):
            # Swap dates if end_date is less than start
            if end < start:
                start, end = end, start

            sales = Sales.query.filter( and_(func.date(Sales.created) == start, Sales.dept == dept)  if start == end else \
            and_(Sales.created >= start, Sales.created <= end, Sales.dept == dept), Sales.deleted == False ).all()
            return sales

        start = datetime.strptime(str(rangeform.start.data), '%Y-%m-%d').date() 
        end = datetime.strptime(str(rangeform.end.data), '%Y-%m-%d').date() 
        # Swap dates if end_date is less than start
        if end < start:
            start, end = end, start
        dept = rangeform.dept.data

        # Query expenses and sales within the date range
        expenses = get_expenses(start, end, dept)
        sales = get_sales(start, end, dept)

        url_ = url_for('main.kitchen_report') if dept == 'k' else url_for('main.cocktail_report')
        dept = 'kitchen' if dept == 'k' else 'cocktail' if dept == 'c' else 'bar'
        #dept = 'kitchen' if dept is 'k' else 'cocktail' if dept is 'c' else 'bar'
        if not sales:
            return jsonify({ 
            #'response': f'Hey!! That Very Sales Is Not Found in ({dept, sales}) Within This Range ({start.strftime("%c")} to {end.strftime("%c")})',
            'response': f'Hey!! That Very Sales Not Found For ({dept}) Within This Range ({start} to {end})',
            'flash':'alert-warning',
            'link': f'{url_}' })

        total_expenses = sum(expense.cost for expense in expenses)
        total_sales = sum(sale.qty * sale.salez.s_price for sale in sales) #bcos price can later change
        #total_sales = sum(sale.total for sale in sales) #so that initially calculated price remains
        #total_sales = sum(x.in_stock * x.item.s_price for x in sales)
        profit = (total_sales - total_expenses) or 0
        #item_count = len(total_expenses) #from-db-count
        report_id = (randint(0, 999999) )

        report = [{ 
        'iid': c.salez.id,  
        'name': c.salez.name,  
        's_price': c.salez.s_price,
        'qty':  c.qty, 
        'total': (c.qty * c.salez.s_price),
        'created':  c.created, } for c in sales]

        return jsonify(
            report, [{ 'report_date_range': f'{start} to {end}',
            'total_expenses': total_expenses, 'total_sales':total_sales, 'profit':profit, 'report_id':report_id}] )
    
    return jsonify({ 
            'response': f'some validation issues {rangeform.errors}  </b>..',
            #'response': f'{type(stockform.cate.data)} invalid { stockform.errors, stockform.data}  </b>..',
            'flash':'alert-warning',
            'link': f''})

@bar.route('/new-sales', methods=['POST'])
@login_required
@db_session_management
def new_sales():
    salesform = SalesForm()
    rangeform = RangeForm()
    referrer =  request.headers.get('Referer')

    item = db.session.query(Sales).join(Items, Sales.item_id==Items.id).filter( and_(Sales.id == sales_id, Sales.deleted == False) ).first()
    if request.method == 'POST':
        #submit = form.year.data if 'year' in request.form  else None, #str
        if "pcs" in request.form:
            #ensure item/item-id & quantity-sold is available
            #if all(value is None or value == 0 for value in (salesform.item_id.data, salesform.pcs.data)):
            if not salesform.item_id.data or not salesform.pcs.data or int(salesform.item_id.data) <= 0 or int(salesform.pcs.data) <= 0:
                return jsonify({ 
                    'response': 'You Have To Select A Product & Also Enter Quantity Sold!',
                    'flash': 'alert-warning',
                    'link': referrer
                })
            
            if salesform.validate_on_submit(): #same-as-post-request
                qty_sold = salesform.pcs.data
                #B4 adding/updating, confirm there's enough stock balance
                if instock == None:
                    return jsonify({ 
                        'response': f'Hey bro, Seems The Product Is\'nt Available Right Now !',
                        'flash':'alert-warning',
                        'link': f'{referrer}'})
                
                 # Check if there are associated Apportion
                
                apportion_items = instock.apportion_items
                if apportion_items:
                    for apportioned_item in apportion_items:
                        available_qty = apportioned_item.items_qty
                        print(f"Apportioned Item ID: {apportioned_item.id}, Items Quantity: {available_qty}")
                    else:
                        print(f"Item ID: {instock.id} has no associated Apportioned Items")
                else:
                    available_qty = instock.in_stock
                    
                #if (instock.in_stock < salesform.pcs.data):
                if (available_qty < qty_sold):

                    if instock.dept == 'k':
                        url_ = url_for('main.kitchen_sales')
                    elif instock.dept == 'c':
                        url_ = url_for('main.cocktail_sales')
                    elif instock.dept == 'b':
                        url_ = url_for('main.bar_sales')
                    else:
                        url_ = referrer   
                    return jsonify(
                        { 
                        'response': f'only <b>({available_qty})</b> left for {instock.name}, you\'ve probably sold ({qty_sold})</b> \
                        but before adding sales, update your stock record  and try again !',
                        'flash':'alert-warning',
                        'link': f'{url_}' 
                        })

                #return f"{salesform.data, item, sales_id, salesform.sales_id.data  }"
                if (item and salesform.is_update.data == True):
                    item.salez.in_stock += item.qty #add-back-deducted-qty-when-sales-was-recorded if item's an update.
                    item.qty = qty_sold #record-as-new-sales
                    item.salez.in_stock -= item.qty  #re-deduct the new-recorded sales
                    item.dept = salesform.dept.data 
                    item.ip = user_ip()
                    db.session.commit()
                    db.session.flush()
                    #flash(f'Success {item.salez.name} updated!', 'success')
                    return jsonify({ 
                        'response': f'Success!!!!, {item.salez.name} updated to {item.qty}  sold !',
                        'flash':'alert-info',
                        'link': ''})
                
                new_sales = Sales( 
                    item_id = item_id,
                    qty=qty_sold, 
                    dept= salesform.dept.data ,
                    salez = instock,
                    )
                
                db.session.add(new_sales)
                db.session.commit()
                db.session.flush()
                db.session.refresh(new_sales) #refresh so-i-can-get-the-last/new-insert-id
                
                new_sales.salez.in_stock -= new_sales.qty
                db.session.commit()

                flash(f'Success africana, you\ve recorded {new_sales.qty} pieces of {new_sales.salez.name} sold !', 'success')
                return jsonify({ 
                    'response': f'Success africana, you have recorded {new_sales.qty} pieces of {new_sales.salez.name} sold !',
                    'flash':'alert-success',
                    'link': f''})
            
            return jsonify({ 
                'response': f'invalid { salesform, salesform.errors, salesform.data}  </b>..',
                'flash':'alert-warning',
                'link': f''})
        
        else:
            return jsonify({ 
                    'response': f'Not Validated { salesform.data, rangeform.data}  </b>..',
                    'flash':'alert-warning',
                    'link': f''})

#//update 
@bar.route('/apportion/<int:item_id>/update', methods=['PUT'])
@login_required
@db_session_management
def update_apportioned(item_id):
    referrer =  request.headers.get('Referer') 
    apportionform = ApportionForm()
    if apportionform.validate_on_submit():
        apportioned_item = Apportion.query.get(item_id)

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
                item = Items.query.get(item_id)
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
@bar.route('/sales/<int:sales_id>/delete', methods=['DELETE'])
def delete(sales_id):
    referrer =  request.headers.get('Referer') 
    #item = db.session.query(Sales).join(Items, Sales.item_id==Items.id).filter( and_(Sales.id == sales_id, Sales.deleted == False) ).first()
    sales = db.session.query(Sales).filter( and_(Sales.id == sales_id, Sales.deleted == False) ).first()
    if request.method == 'DELETE' and sales != None:
        sales.deleted = True
        db.session.commit()
        db.session.flush()
        #db.session.refresh()
        return jsonify({ 
            'response': f'Hey!! you\'ve deleted {sales.salez.name}',
            'flash':'alert-danger',
            'link': f'{referrer}'
            })

