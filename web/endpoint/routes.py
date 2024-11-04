from datetime import datetime
from random import randint
from flask import jsonify, Blueprint, request, url_for, flash
from flask_login import current_user, login_required

from sqlalchemy import and_, or_
from sqlalchemy.sql import func

from web import db, csrf
from web.main.forms import CateForm, ExpensesForm, StockForm, SalesForm, RangeForm

from web.models import Category, Expenses, Items, StockHistory, Notification, Sales
from web.utils.ip_adrs import user_ip
from web.utils.sequence_int import generator
from web.utils.db_session_management import db_session_management
# from web.extensions import cache, csrf

endpoint = Blueprint('endpoint', __name__)
def exclude_deleted(query):
    return query.filter_by(deleted=False)

@endpoint.route('/new-stock-0', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<string:action>/new-stock-0', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def stock_action_0(item_id=None, action=None):
    stockform = StockForm()
    action, item_id,  = request.args.get('action', action ) , request.args.get('item_id', item_id )
    it = exclude_deleted(Items.query.filter( (Items.id == item_id) | (Items.id == stockform.item_id.data)) ).first()

    referrer =  request.headers.get('Referer') 
    if request.method == 'DELETE' and it != None and action == 'del':

        it.deleted = True
        db.session.commit()
        
        flash(f'Success {it.name} Deleted!', 'danger')
        return jsonify({ 
            'response': f'Hey!! You\'ve deleted {it.name}',
            'flash':'alert-danger',
            'link': f'{referrer}'})
    
    if not stockform.validate_on_submit(): #same-as-post-request
        return jsonify({ 
            'response': f'Error { stockform.errors, stockform.cate.data}  </b>..',
            #'response': f'{type(stockform.cate.data)} invalid { stockform.errors, stockform.data}  </b>..',
            'flash':'alert-warning',
            'link': f'{referrer}'})
        
    if stockform.validate_on_submit(): #same-as-post-request
        if item_id or stockform.item_id.data: 
            #backup-stock-history when B4 updating of the Item/Stock Record.
            
            if stockform.in_stock.data < 0:
                deduction_amount = abs(stockform.in_stock.data)  # Absolute value of reduction
                # Record the deduction in stock history
                saved_history = StockHistory(
                    user_id=it.user_id or current_user.id if current_user.is_authenticated else 0,
                    item_id=it.id,
                    item=it,
                    version=generator.next(),
                    difference=-deduction_amount,  # Negative value for reduction
                    in_stock=it.in_stock - deduction_amount,  # Deduct the reduction
                    desc=f"{current_user.username} reduced stock by <{deduction_amount}> for {it.name} on {it.updated}"
                )
            else:
                saved_history = StockHistory(
                    user_id = it.user_id or current_user.id if current_user.is_authenticated else 0,
                    item_id = it.id,
                    version = generator.next(), #i created a func in utils.py to generate a sequencial int for me
                    item = it,
                    difference = stockform.in_stock.data or 0,
                    in_stock = it.in_stock, 
                    desc = f"{it.name} was initially ({it.in_stock or 0}) as at {it.updated}"
                    )
                    #db.session.add(saved_history)

            it.user_id = current_user.id if current_user.is_authenticated else 0
            it.name=stockform.name.data
            it.in_stock +=  stockform.in_stock.data or 0
            it.new_stock = stockform.new_stock.data if 'new_stock' in request.form else 0
            it.c_price = stockform.c_price.data if 'c_price' in request.form else 0
            it.s_price = stockform.s_price.data
            it.cate = stockform.cate.data
            it.ip = user_ip()
            it.deleted = False #This would ensure unique constraints defined under Items() model also works by excluding the deleted columns

            db.session.add(saved_history)
            db.session.commit()
            db.session.flush()
            db.session.refresh(saved_history) #refresh so-i-can-get-the-last/new-insert-id
            
            #flash(f'Success {it.name} updated!', 'success')
            return jsonify({ 
                'response': f'Success {it.name} updated!',
                'flash':'alert-success',
                'link': f'{referrer}'})
        

        saved_stock = Items(
            user_id = current_user.id if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
            #cate = selected_cate,
            category = stockform.cate.data,
            name=stockform.name.data, 
            in_stock=stockform.in_stock.data or 0, 
            new_stock=stockform.new_stock.data if 'new_stock' in request.form else 0, #on-my-latest-updates-this-field-is-ignored
            c_price=stockform.c_price.data if 'c_price' in request.form else 0, 
            s_price=stockform.s_price.data, 
            dept=stockform.dept.data if 'dept' in request.form else 'k', 
            ip = user_ip(),
            deleted = False #This would ensure unique constraints defined under Items() model also works by excluding the deleted columns

            )

        #backup-stock-history when recording for the first time.
        saved_history = StockHistory(
            user_id = saved_stock.user_id or current_user.id if current_user.is_authenticated else 0,
            item_id = saved_stock.id,
            item = saved_stock,
            version = generator.next(), #i created a func in utils.py to generate a sequencial int for me
            difference = saved_stock.in_stock,
            in_stock=saved_stock.in_stock, 
            desc = f"{current_user.username} added <{saved_stock.in_stock}> of {saved_stock.name} on {saved_stock.updated}"
            )
        db.session.add(saved_history)
        db.session.add(saved_stock)
        db.session.commit()
        db.session.flush()
        db.session.refresh(saved_stock) #refresh so-i-can-get-the-last/new-insert-id

        """ #backup-stock-history when recording for the first time.
        saved_history = StockHistory(
            user_id = saved_stock.user_id or current_user.id if current_user.is_authenticated else 0,
            item_id = saved_stock.id,
            item = saved_stock,
            version = generator.next(), #i created a func in utils.py to generate a sequencial int for me
            difference = saved_stock.in_stock,
            in_stock=saved_stock.in_stock, 
            desc = f"{current_user.username} added <{saved_stock.in_stock}> of {saved_stock.name} on {saved_stock.updated}"
            )
        db.session.add(saved_history)
        db.session.commit()
        db.session.flush()
        db.session.refresh(saved_history) #refresh so-i-can-get-the-last/new-insert-id """

        flash(f'Success {saved_stock.name} Added!', 'success')
        return jsonify( { 
            'response': f'Success ..<b class="info"> {saved_stock.name}</b>.. Added!!',
            'flash':'alert-success',
            'link': f''})

@endpoint.route('/new-stock', methods=['POST', 'PUT', 'DELETE', 'GET'])
@endpoint.route('/<int:item_id>/<string:action>/new-stock', methods=['POST', 'GET', 'PUT', 'DELETE'])
@login_required
@db_session_management
def stock_action(item_id=None, action=None):
    stockform = StockForm()
    
    action, item_id = request.args.get('action', action), request.args.get('item_id', item_id)
    referrer = request.headers.get('Referer')
    
    # Handle form validation errors
    if request.method in ['POST', 'PUT'] and not stockform.validate_on_submit():
        return jsonify_error_response(stockform.errors, referrer)
    
    # Retrieve the item based on ID, excluding deleted ones
    item = get_item(item_id, stockform.item_id.data)
    
    # Handle DELETE
    if request.method == 'DELETE' and action == 'del' and item:
        return delete_item(item, referrer)
    
    # Handle PUT and POST (update or create item)
    if request.method in ['POST', 'PUT']:
        return process_item(stockform, item, referrer)

    return jsonify({'response': 'Invalid request', 'flash': 'alert-danger'})

def get_item(item_id, form_item_id):
    """ Retrieve item based on item_id or form data """
    return exclude_deleted(Items.query.filter((Items.id == item_id) | (Items.id == form_item_id))).first()

def delete_item(item, referrer):
    """ Delete an item and record the deletion """
    item.deleted = True
    # db.session.delete(item)
    save_stock_history(item, item.in_stock, f"{current_user.username} deleted {item.name}")
    db.session.commit()
    return jsonify({
        'response': f'Hey!! You\'ve deleted {item.name}',
        'flash': 'alert-danger',
        'link': referrer
    })

def process_item(stockform, item, referrer):
    """ Process creation or update of item """
    if item:
        # Update existing item
        return update_item(item, stockform, referrer)
    else:
        # Create a new item
        return create_item(stockform, referrer)

def create_item(stockform, referrer):
    """ Create a new stock item and save history """
    new_item = Items(
        user_id=current_user.id if current_user.is_authenticated else 0,
        name=stockform.name.data,
        in_stock=stockform.in_stock.data or 0,
        new_stock=stockform.new_stock.data or 0,
        c_price=stockform.c_price.data or 0,
        s_price=stockform.s_price.data,
        category_id=stockform.cate.data,
        dept=stockform.dept.data or 'k',
        ip=user_ip(),
        deleted=False
    )
    db.session.add(new_item)
    save_stock_history(new_item, new_item.in_stock, f"{current_user.username} added {new_item.in_stock} of {new_item.name}")
    db.session.commit()
    return jsonify({
        'response': f'Success ..<b class="info"> {new_item.name}</b>.. Added!!',
        'flash': 'alert-success',
        'link': referrer
    })

def update_item(item, stockform, referrer):
    """ Update an existing stock item and save history """
    
    if stockform.in_stock.data is not None:
        try:
            # Check if in_stock data is a number directly; if not, evaluate it as an expression
            if isinstance(stockform.in_stock.data, (int, float)):
                in_stock_value = stockform.in_stock.data
            else:
                # Ensure that we only evaluate safe and complete expressions
                expression = str(stockform.in_stock.data).strip()
                
                # Basic validation to prevent invalid syntax
                if expression and (expression[-1].isdigit() or expression[-1] in ')'):
                    # Attempt to safely evaluate expressions
                    in_stock_value = eval(expression, {"__builtins__": None}, {})
                else:
                    raise ValueError("Invalid expression format. Enter correct extpression/quantity format")

            # Check if the evaluated value is negative
            if in_stock_value < 0:
                raise ValueError("Stock cannot be less than zero.")

            # Update stock with evaluated value
            item.in_stock = in_stock_value
            save_stock_history(item, in_stock_value, f"{item.name} stock updated to {item.in_stock} by {current_user.username}")
        except (NameError, SyntaxError, TypeError, ValueError) as e:
            # Handle evaluation errors and provide feedback
            return jsonify({
                'response': f'Error evaluating in_stock: {str(e)}',
                'flash': 'alert-danger',
                'link': referrer
            })

    # Update other fields
    item.user_id = current_user.id if current_user.is_authenticated else 0
    item.name = stockform.name.data
    item.new_stock = stockform.new_stock.data or 0
    item.c_price = stockform.c_price.data or 0
    item.s_price = stockform.s_price.data
    item.category_id = stockform.cate.data
    item.ip = user_ip()
    item.deleted = False

    db.session.commit()
    return jsonify({
        'response': f'Success {item.name} updated!',
        'flash': 'alert-success',
        'link': referrer
    })

def update_item_04(item, stockform, referrer):
    """ Update an existing stock item and save history """
    
    if stockform.in_stock.data is not None:
        try:
            # Check if in_stock data is a number directly; if not, evaluate it as an expression
            if isinstance(stockform.in_stock.data, (int, float)):
                in_stock_value = stockform.in_stock.data
            else:
                # Attempt to safely evaluate expressions
                in_stock_value = eval(str(stockform.in_stock.data), {"__builtins__": None}, {})

            # Update stock with evaluated value
            item.in_stock = in_stock_value
            save_stock_history(item, in_stock_value, f"{item.name} stock updated to {item.in_stock} by {current_user.username}")
        except (NameError, SyntaxError, TypeError, ValueError) as e:
            # Handle evaluation errors and provide feedback
            return jsonify({
                'response': f'Error evaluating in_stock: {str(e)}',
                'flash': 'alert-danger',
                'link': referrer
            })

    # Update other fields
    item.user_id = current_user.id if current_user.is_authenticated else 0
    item.name = stockform.name.data
    item.new_stock = stockform.new_stock.data or 0
    item.c_price = stockform.c_price.data or 0
    item.s_price = stockform.s_price.data
    item.category_id = stockform.cate.data
    item.ip = user_ip()
    item.deleted = False

    db.session.commit()
    return jsonify({
        'response': f'Success {item.name} updated!',
        'flash': 'alert-success',
        'link': referrer
    })

def update_item_03(item, stockform, referrer):
    """ Update an existing stock item and save history """
    
    if stockform.in_stock.data is not None:
        try:
            # Use ast.literal_eval() instead of eval() for safety
            # items_qty_eval = eval(stockform.in_stock.data)
            items_qty_eval = eval(stockform.in_stock.data, {"__builtins__": None}, {})
            if isinstance(items_qty_eval, (int, float)):  # Ensure the evaluated result is numeric
                item.in_stock = items_qty_eval
                save_stock_history(item, items_qty_eval, f"{item.name} stock updated to {item.in_stock} by {current_user.username}")
            else:
                raise ValueError("Stock quantity must be a number.")
        except Exception as e:
            return jsonify({
                'response': f'Error evaluating in_stock: {str(e)}',
                'flash': 'alert-danger',
                'link': referrer
            })
                    
    # Update other fields
    item.user_id = current_user.id if current_user.is_authenticated else 0
    item.name = stockform.name.data
    item.new_stock = stockform.new_stock.data or 0
    item.c_price = stockform.c_price.data or 0
    item.s_price = stockform.s_price.data
    item.category_id = stockform.cate.data
    item.ip = user_ip()
    item.deleted = False
    
    db.session.commit()
    return jsonify({
        'response': f'Success {item.name} updated!',
        'flash': 'alert-success',
        'link': referrer
    })

def update_item_02(item, stockform, referrer):
    """ Update an existing stock item and save history """
    
    # if stockform.in_stock.data < 0:
    #     # Deduct from stock
    #     deduction_amount = abs(stockform.in_stock.data)
    #     item.in_stock -= deduction_amount
    #     save_stock_history(item, -deduction_amount, f"{current_user.username} reduced stock by {deduction_amount} for {item.name}")
    # else:
    #     # Add to stock
    #     item.in_stock += stockform.in_stock.data
    #     save_stock_history(item, stockform.in_stock.data, f"{item.name} updated stock to {item.in_stock}")

    if stockform.in_stock.data is not None:
        try:
            items_qty_eval = eval(stockform.in_stock.data, {"__builtins__": None}, {})
            item.in_stock = items_qty_eval
            save_stock_history(item, stockform.in_stock.data, f"{item.name} updated stock to {item.in_stock} by {current_user.username}")
        except Exception as e:
            return jsonify({
                'response': f'Error evaluating items_qty: {str(e)}',
                'flash': 'alert-danger',
                'link': referrer
            })
                    
    # Update other fields
    item.user_id = current_user.id if current_user.is_authenticated else 0
    item.name = stockform.name.data
    item.new_stock = stockform.new_stock.data or 0
    item.c_price = stockform.c_price.data or 0
    item.s_price = stockform.s_price.data
    item.category_id = stockform.cate.data
    item.ip = user_ip()
    item.deleted = False
    
    db.session.commit()
    return jsonify({
        'response': f'Success {item.name} updated!',
        'flash': 'alert-success',
        'link': referrer
    })

def save_stock_history(item, difference, description):
    """ Save history for stock updates """
    stock_history = StockHistory(
        user_id=current_user.id if current_user.is_authenticated else 0,
        item_id=item.id,
        version=generator.next(),
        item=item,
        difference=difference,
        in_stock=item.in_stock,
        desc=description
    )
    db.session.add(stock_history)
    
def jsonify_error_response(errors, referrer):
    """ Handle validation errors """
    return jsonify({
        'response': f'Error {errors}',
        'flash': 'alert-warning',
        'link': referrer
    })

@endpoint.route('/sales-0', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<int:sales_id>/<string:action>/sales-0', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def sales_action_0(item_id=None, sales_id=None, action=None):
    salesform = SalesForm()
    rangeform = RangeForm()
    referrer = request.headers.get('Referer') 

    action = request.args.get('action', action) 
    item_id = request.args.get('item_id', item_id) or salesform.item_id.data
    sales_id = request.args.get('sales_id', sales_id) or (salesform.sales_id.data if 'sales_id' in request.form else None)

    # Query for sales and item in stock
    sale_record = db.session.query(Sales).join(Items, Sales.item_id == Items.id).filter(and_(Sales.id == sales_id, Sales.deleted == False)).first()
    item_in_stock = Items.query.filter(Items.id == item_id, Items.deleted == False).first()

    if request.method == 'DELETE' and sale_record is not None and action == 'del':
        sale_record.deleted = True
        db.session.commit()
        flash(f'Success, {sale_record.item.name} Deleted!', 'danger')
        return jsonify({
            'response': f'You have deleted {sale_record.item.name}',
            'flash': 'alert-danger',
            'link': f'{referrer}'
        })

    if request.method == 'POST':
        pcs_sold = int(salesform.pcs_sold.data) if salesform.pcs_sold.data is not None else None
        pcs_left = int(salesform.pcs_left.data) if salesform.pcs_left.data is not None else None

        if not salesform.item_id.data or pcs_left is None or int(salesform.item_id.data) <= 0:
            return jsonify({
                'response': "Select a product and provide the closing stock to calculate sales.",
                'flash': 'alert-warning',
                'link': referrer
            })

        if salesform.validate_on_submit():
            # Check if there's enough stock available
            if item_in_stock is None:
                return jsonify({
                    'response': 'No stock available for this product. Please update the stock records first.',
                    'flash': 'alert-warning',
                    'link': referrer
                })

            # Handle apportioned items
            apportioned_items = item_in_stock.apportion_items
            available_qty = item_in_stock.in_stock
            if apportioned_items:
                total_apportioned_qty = sum(item.items_qty for item in apportioned_items)
                available_qty += total_apportioned_qty

            if pcs_left <= 0:
                qty_sold = available_qty  # Sold everything
            elif pcs_left < available_qty:
                qty_sold = available_qty - pcs_left
            elif pcs_left > available_qty:
                return jsonify({
                    'response': f'Closing stock of {pcs_left} exceeds current stock of {available_qty}. Please update your records.',
                    'flash': 'alert-warning',
                    'link': referrer
                })
            else:
                return jsonify({
                    'response': 'No changes in stock. The closing stock equals current stock.',
                    'flash': 'alert-warning',
                    'link': referrer
                })

            if qty_sold is None:
                return jsonify({
                    'response': 'Please provide either a closing stock or quantity sold.',
                    'flash': 'alert-warning',
                    'link': referrer
                })

            if qty_sold == 0:
                return jsonify({
                    'response': f'No sales recorded as stock level is {available_qty}.',
                    'flash': 'alert-warning',
                    'link': referrer
                })

            if available_qty < qty_sold:
                return jsonify({
                    'response': f'Insufficient stock. You have {available_qty} units available but tried to sell {qty_sold}.',
                    'flash': 'alert-warning',
                    'link': referrer
                })

            # Update apportioned stock
            if apportioned_items:
                remaining_qty_to_deduct = qty_sold
                for apportioned_item in apportioned_items:
                    if remaining_qty_to_deduct <= 0:
                        break

                    if apportioned_item.items_qty >= remaining_qty_to_deduct:
                        apportioned_item.items_qty -= remaining_qty_to_deduct
                        remaining_qty_to_deduct = 0
                    else:
                        remaining_qty_to_deduct -= apportioned_item.items_qty
                        apportioned_item.items_qty = 0

                db.session.commit()

            # Update or add new sale
            if sale_record and salesform.is_update.data:
                sale_record.item.in_stock += sale_record.qty  # Add back the original quantity
                sale_record.qty_left = pcs_left
                sale_record.qty = qty_sold
                sale_record.item.in_stock -= sale_record.qty  # Deduct the updated sales quantity
                db.session.commit()
                return jsonify({
                    'response': f'Success! {sale_record.item.name} updated with {sale_record.qty} units sold!',
                    'flash': 'alert-info',
                    'link': ''
                })

            new_sale = Sales(
                item_id=item_id,
                qty_left=pcs_left,
                qty=qty_sold,
                dept=salesform.dept.data,
                item=item_in_stock,
                # 
                title=item_in_stock.name,
                price= item_in_stock.s_price,
                total= qty_sold * item_in_stock.s_price
            )
            db.session.add(new_sale)
            db.session.commit()

            new_sale.item.in_stock -= new_sale.qty
            db.session.commit()

            return jsonify({
                'response': f'Success! {new_sale.qty} units of {new_sale.item.name} sold!',
                'flash': 'alert-success',
                'link': ''
            })

        return jsonify({
            'response': f'Form validation failed: {salesform.errors}',
            'flash': 'alert-warning',
            'link': ''
        })

"""
@endpoint.route('/sales', methods=['POST', 'PUT', 'DELETE', 'GET'])
@endpoint.route('/<int:item_id>/<int:sales_id>/<string:action>/sales', methods=['POST', 'GET', 'PUT', 'DELETE'])
@login_required
@db_session_management
def sales_action(item_id=None, sales_id=None, action=None):
    sales_form = SalesForm()
    referrer = request.headers.get('Referer')

    # Get action and IDs from request arguments if not provided
    action = request.args.get('action', action)
    item_id = request.args.get('item_id', item_id) or sales_form.item_id.data
    sales_id = request.args.get('sales_id', sales_id) or (sales_form.sales_id.data if 'sales_id' in request.form else None)

    # Retrieve the sale record and item in stock
    sale_record = db.session.query(Sales).join(Items, Sales.item_id == Items.id).filter(Sales.id == sales_id, Sales.deleted == False).first()
    item_in_stock = Items.query.filter(Items.id == item_id, Items.deleted == False).first()

    # Handle delete request
    if request.method == 'DELETE' and sale_record and action == 'del':
        return delete_sale_record(sale_record, referrer)

    # Handle post request
    if request.method == 'POST':
        return handle_post_request(sales_form, item_in_stock, referrer, sale_record)

    return jsonify({'response': 'Invalid request method', 'flash': 'alert-danger'}), 405

def delete_sale_record(sale_record, referrer):
    sale_record.deleted = True
    db.session.delete(sale_record)
    db.session.commit()
    flash(f'Success, {sale_record.item.name} deleted!', 'danger')
    return jsonify({
        'response': f'You have deleted {sale_record.item.name}',
        'flash': 'alert-danger',
        'link': referrer
    })

def handle_post_request(sales_form, item_in_stock, referrer, sale_record):
    pcs_sold = int(sales_form.pcs_sold.data or 0)
    pcs_left = int(sales_form.pcs_left.data) if sales_form.pcs_left.data is not None else 0

    # update stock quantity to be sub of current_stock + sales qty if it's an update ie sales_record if. Commented out here 
    # cos it affects other post requests like direct sales.
    # item_in_stock.in_stock += sale_record.qty if sale_record else item_in_stock.in_stock
    
    qty_sold, available_qty = calculate_sold_quantity(pcs_left, item_in_stock)

    if qty_sold is None:
        return jsonify({
            'response': f'Closing stock of {pcs_left} exceeds current stock of {available_qty}. Please update your records.',
            'flash': 'alert-warning',
            'link': referrer
        })
        
    if not sales_form.item_id.data or pcs_left <= 0:
        return response_message(
            "Select a product and provide the closing stock to calculate sales.",
            'alert-warning', referrer
        )

    if not sales_form.validate_on_submit():
        return response_message(
            f'Form validation failed: {sales_form.errors}',
            'alert-warning', ''
        )

    if not item_in_stock:
        return response_message(
            "No stock available for this product. Please update the stock records first.",
            'alert-warning', referrer
        )

    # Check available quantity and calculate sold quantity
    qty_sold, available_qty = calculate_sold_quantity(pcs_left, item_in_stock)
    if qty_sold is None:
        return qty_sold  # Returns appropriate JSON response

    # Update apportioned stock if necessary
    update_apportioned_stock(qty_sold, item_in_stock)

    # Update or add new sale record
    if sale_record and sales_form.is_update.data:
        return update_sale_record(sale_record, pcs_left, qty_sold)

    return add_new_sale(sales_form=sales_form, item_id=sales_form.item_id.data,\
        pcs_left=pcs_left, qty_sold=qty_sold, item_in_stock=item_in_stock)

def add_new_sale(item_id, pcs_left, qty_sold, item_in_stock, sales_form):
    new_sale = Sales(
        item_id=item_id,
        qty_left=pcs_left,
        qty=qty_sold,
        dept=sales_form.dept.data,
        item=item_in_stock,
        title=item_in_stock.name,
        price=item_in_stock.s_price,
        total=qty_sold * item_in_stock.s_price
    )
    db.session.add(new_sale)
    db.session.commit()

    new_sale.item.in_stock -= new_sale.qty
    db.session.commit()

    return jsonify({
        'response': f'Success! {new_sale.qty} units of {new_sale.item.name} sold!',
        'flash': 'alert-success',
        'link': ''
    })

def calculate_sold_quantity(pcs_left, item_in_stock):
    
    if item_in_stock is None:
        # Instead of returning jsonify here, raise an exception or return an error flag with the tuple
        return None, None  # or raise ValueError("No stock available") if you'd like to handle it as an error

    apportioned_items = item_in_stock.apportion_items
    available_qty = item_in_stock.in_stock
    if apportioned_items:
        total_apportioned_qty = sum(item.items_qty for item in apportioned_items)
        available_qty += total_apportioned_qty

    if pcs_left <= 0:
        qty_sold = available_qty
    elif pcs_left < available_qty:
        qty_sold = available_qty - pcs_left
    elif pcs_left > available_qty:
        # Handle the error by returning an indicator, e.g., `None, available_qty`
        return None, available_qty
    else:
        qty_sold = 0

    return qty_sold, available_qty

def update_apportioned_stock(qty_sold, item_in_stock):
    remaining_qty = qty_sold
    for apportioned_item in item_in_stock.apportion_items:
        if remaining_qty <= 0:
            break
        if apportioned_item.items_qty >= remaining_qty:
            apportioned_item.items_qty -= remaining_qty
            remaining_qty = 0
        else:
            remaining_qty -= apportioned_item.items_qty
            apportioned_item.items_qty = 0
    db.session.commit()

def update_sale_record(sale_record, pcs_left, qty_sold):
    
    sale_record.item.in_stock += sale_record.qty  # Add back the original quantity
    sale_record.qty_left = pcs_left
    sale_record.qty = qty_sold
    sale_record.item.in_stock -= sale_record.qty  # Deduct the updated sales quantity
    db.session.commit()
    return jsonify({
        'response': f'Success! {sale_record.item.name} updated with {sale_record.qty} units sold!',
        'flash': 'alert-info',
        'link': ''
    })

def response_message(message, flash_type, link):
    return jsonify({'response': message, 'flash': flash_type, 'link': link})
"""

# ===================================================================


# Define the endpoint routes for sales actions
@endpoint.route('/sales', methods=['POST', 'PUT', 'DELETE', 'GET'])
@endpoint.route('/<int:item_id>/<int:sales_id>/<string:action>/sales', methods=['POST', 'GET', 'PUT', 'DELETE'])
@login_required
@db_session_management
def sales_action(item_id=None, sales_id=None, action=None):
    sales_form = SalesForm()
    referrer = request.headers.get('Referer')
    
    # Extract action and IDs from request args if not provided in the URL
    action = request.args.get('action', action)
    item_id = request.args.get('item_id', item_id) or sales_form.item_id.data
    sales_id = request.args.get('sales_id', sales_id) or (sales_form.sales_id.data if 'sales_id' in request.form else None)

    # Retrieve sale record and item in stock
    sale_record = db.session.query(Sales).join(Items, Sales.item_id == Items.id).filter(Sales.id == sales_id, Sales.deleted == False).first()
    item_in_stock = Items.query.filter(Items.id == item_id, Items.deleted == False).first()

    # Handle delete request
    if request.method == 'DELETE' and sale_record and action == 'del':
        return delete_sale_record(sale_record, referrer)

    # Handle update request (PUT)
    if request.method == 'PUT' and sale_record or sale_record and sales_form.is_update.data:
        return handle_update_request(sales_form, item_in_stock, sale_record)

    # Handle new sale (POST)
    if request.method == 'POST':
        return handle_post_request(sales_form, item_in_stock, referrer)

    return jsonify({'response': 'Invalid request method', 'flash': 'alert-danger'}), 405


# Function to handle delete operation on a sale record
def delete_sale_record(sale_record, referrer):
    # sale_record.deleted = True
    db.session.delete(sale_record)
    db.session.commit()
    flash(f'Success, {sale_record.item.name} deleted!', 'danger')
    return jsonify({
        'response': f'You have deleted {sale_record.item.name}',
        'flash': 'alert-danger',
        'link': referrer
    })

# Function to handle post requests to create a new sale
def handle_post_request(sales_form, item_in_stock, referrer):
    # pcs_sold = int(sales_form.pcs_sold.data or 0)
    pcs_left = int(sales_form.pcs_left.data) if sales_form.pcs_left.data is not None else 0

    qty_sold, available_qty = calculate_sold_quantity(pcs_left, item_in_stock)

    if qty_sold is None:
        return jsonify({
            'response': f'Closing stock of {pcs_left} exceeds current stock of {available_qty}. Please update your records.',
            'flash': 'alert-warning',
            'link': referrer
        })
        
    if not sales_form.item_id.data or pcs_left <= 0:
        return response_message(
            f"Select a product and provide the closing stock to calculate sales.{sales_form.__dict__}",
            'alert-warning', referrer
        )

    if not sales_form.validate_on_submit():
        return response_message(
            f'Form validation failed: {sales_form.errors}',
            'alert-warning', ''
        )

    if not item_in_stock:
        return response_message(
            "No stock available for this product. Please update the stock records first.",
            'alert-warning', referrer
        )

    # Add new sale record
    return add_new_sale(
        sales_form=sales_form,
        item_id=sales_form.item_id.data,
        pcs_left=pcs_left,
        qty_sold=qty_sold,
        item_in_stock=item_in_stock
    )

# Function to handle update requests on an existing sale record
def handle_update_request(sales_form, item_in_stock, sale_record):
    pcs_left = int(sales_form.pcs_left.data or 0)
    
    qty_sold, available_qty = calculate_sold_quantity(pcs_left, item_in_stock)

    if qty_sold is None:
        return jsonify({
            'response': f'Closing stock of {pcs_left} exceeds current stock of {available_qty}. Please update your records.',
            'flash': 'alert-warning'
        })

    # Ensure form validation
    if not sales_form.validate_on_submit():
        return response_message(
            f'Form validation failed: {sales_form.errors}',
            'alert-warning', ''
        )

    # Update sale record logic
    sale_record.item.in_stock += sale_record.qty  # Restore original stock
    sale_record.qty_left = pcs_left
    sale_record.qty = qty_sold
    sale_record.item.in_stock -= sale_record.qty  # Deduct updated quantity

    db.session.commit()

    return jsonify({
        'response': f'Success! {sale_record.item.name} updated with {sale_record.qty} units sold!',
        'flash': 'alert-info'
    })


# Function to add a new sale record
def add_new_sale(sales_form, item_id, pcs_left, qty_sold, item_in_stock):
    new_sale = Sales(
        item_id=item_id,
        qty_left=pcs_left,
        qty=qty_sold,
        dept=sales_form.dept.data,
        item=item_in_stock,
        title=item_in_stock.name,
        price=item_in_stock.s_price,
        total=qty_sold * item_in_stock.s_price
    )
    db.session.add(new_sale)
    db.session.commit()

    # Deduct quantity from stock
    new_sale.item.in_stock -= new_sale.qty
    db.session.commit()

    return jsonify({
        'response': f'Success! {new_sale.qty} units of {new_sale.item.name} sold!',
        'flash': 'alert-success',
        'link': ''
    })


# Function to calculate sold quantity based on closing stock
def calculate_sold_quantity(pcs_left, item_in_stock):
    if item_in_stock is None:
        return None, None  # No stock available

    apportioned_items = item_in_stock.apportion_items
    available_qty = item_in_stock.in_stock
    if apportioned_items:
        total_apportioned_qty = sum(item.items_qty for item in apportioned_items)
        available_qty += total_apportioned_qty

    if pcs_left <= 0:
        qty_sold = available_qty
    elif pcs_left < available_qty:
        qty_sold = available_qty - pcs_left
    elif pcs_left > available_qty:
        return None, available_qty
    else:
        qty_sold = 0

    return qty_sold, available_qty

# Function to update apportioned stock based on quantity sold
def update_apportioned_stock(qty_sold, item_in_stock):
    remaining_qty = qty_sold
    for apportioned_item in item_in_stock.apportion_items:
        if remaining_qty <= 0:
            break
        if apportioned_item.items_qty >= remaining_qty:
            apportioned_item.items_qty -= remaining_qty
            remaining_qty = 0
        else:
            remaining_qty -= apportioned_item.items_qty
            apportioned_item.items_qty = 0
    db.session.commit()

# Helper function to generate JSON response messages
def response_message(message, flash_type, link):
    return jsonify({'response': message, 'flash': flash_type, 'link': link})


"""  ============================================ """
from flask import jsonify, request, url_for
from sqlalchemy import and_, func
from datetime import datetime
from random import randint
from sqlalchemy.exc import SQLAlchemyError

@endpoint.route('/sales_report', methods=['POST'])
# @login_required
@csrf.exempt
def generate_sales_report():
    rangeform = RangeForm()

    try:
        # Check if form data includes start and end dates
        if "start" in request.form and "end" in request.form:
            if rangeform.validate_on_submit():
                
                def get_expenses(start, end, dept):
                    # Swap dates if end_date is less than start
                    if end < start:
                        start, end = end, start
                    xp = Expenses.query.filter(and_(
                        func.date(Expenses.created) == start if start == end else Expenses.created.between(start, end),
                        Expenses.dept == dept,
                        Expenses.deleted == False
                    )).all()
                    return xp

                def get_sales(start, end, dept):
                    # Swap dates if end_date is less than start
                    if end < start:
                        start, end = end, start
                    sales = Sales.query.filter(and_(
                        func.date(Sales.created) == start if start == end else Sales.created.between(start, end),
                        Sales.dept == dept,
                        Sales.deleted == False
                    ) ).all()
                    return sales

                # Parse dates from the form
                start = datetime.strptime(str(rangeform.start.data), '%Y-%m-%d').date()
                end = datetime.strptime(str(rangeform.end.data), '%Y-%m-%d').date()
                
                if end < start:
                    start, end = end, start  # Swap if end date is before start date

                dept = rangeform.dept.data
                # Normalize department codes ('k', 'c', etc.)
                url_ = url_for('main.kitchen_report') if dept == 'k' else url_for('main.cocktail_report')
                dept_name = 'kitchen' if dept == 'k' else 'cocktail' if dept == 'c' else 'bar'

                # Query expenses and sales in the given range
                expenses = get_expenses(start, end, dept)
                sales = get_sales(start, end, dept)

                # Check if sales are found within the date range
                if not sales:
                    return jsonify({
                        'response': f'No sales found for {dept_name} within this range {start} to {end}.',
                        'flash': 'alert-warning',
                        'link': url_
                    })

                # Calculate totals
                total_expenses = sum(expense.cost for expense in expenses)
                total_sales = sum(sale.qty * sale.item.s_price for sale in sales)  # Calculate based on quantity and selling price
                profit = total_sales - total_expenses

                # Generate a report ID
                report_id = randint(0, 999999)

                # Format the report data
                report = [{
                    'iid': sale.item.id,
                    'name': sale.item.name,
                    's_price': sale.item.s_price,
                    'qty': sale.qty,
                    'total': sale.qty * sale.item.s_price,
                    'created': sale.created
                } for sale in sales]

                # Return the report as a JSON response
                return jsonify(report, [{
                    'report_date_range': f'{start} to {end}',
                    'total_expenses': total_expenses,
                    'total_sales': total_sales,
                    'profit': profit,
                    'report_id': report_id
                }])

            # Handle form validation errors
            return jsonify({
                'response': f'Form validation issues: {rangeform.errors}',
                'flash': 'alert-warning',
                'link': ''
            })

        # Handle missing form data
        return jsonify({
            'response': 'No valid data found in the request.',
            'flash': 'alert-warning',
            'link': ''
        })

    except ValueError as ve:
        return jsonify({
            'response': f'Error in date processing: {str(ve)}',
            'flash': 'alert-danger',
            'link': ''
        })
    except SQLAlchemyError as db_err:
        return jsonify({
            'response': f'Database error occurred: {str(db_err)}',
            'flash': 'alert-danger',
            'link': ''
        })
    except Exception as e:
        return jsonify({
            'response': f'An unexpected error occurred: {str(e)}',
            'flash': 'alert-danger',
            'link': ''
        })

""" ================================================ """

@endpoint.route('/new-xpenses', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<string:action>/new-xpenses', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def xpenses_action(item_id=None, action=None):
    xpenseform = ExpensesForm()
    rangeform = RangeForm()
    referrer =  request.headers.get('Referer')

    action, item_id,  = request.args.get('action', action ) , request.args.get('item_id', item_id)

    it = Expenses.query.filter(or_(Expenses.id == item_id, Expenses.id == xpenseform.item_id.data), Expenses.deleted == False ).first()
    
    if request.method == 'DELETE' and it != None and action == 'del':
        it.deleted = True
        db.session.commit()
        flash(f'Success {it.cost} Deleted!', 'danger')
        return jsonify({ 
            'response': f'Hey!! You\'ve deleted {it.cost} Spent on {it.created}',
            'flash':'alert-danger',
            'link': f'{referrer}'})
    
    if xpenseform.validate_on_submit(): #same-as-post-request

        if (item_id or xpenseform.item_id.data) and it != None: 
            it.cost = xpenseform.cost.data
            it.comment = xpenseform.comment.data
            it.created = xpenseform.created.data
            it.dept = xpenseform.dept.data
            db.session.commit()
            flash(f'Success {it.cost} updated!', 'success')
            return jsonify({ 
                'response': f'Success {it.cost} updated!',
                'flash':'alert-success',
                'link': f'{referrer}'})

        new_xpenses = Expenses( 
            cost = xpenseform.cost.data,
            comment=xpenseform.comment.data, 
            dept=xpenseform.dept.data, 
            )
        db.session.add(new_xpenses)
        db.session.commit()
        db.session.flush()
        db.session.refresh(new_xpenses) #refresh so-i-can-get-the-last/new-insert-id
        flash(f'Success {new_xpenses.cost} Added!', 'success')
        return jsonify( { 
            'response': f'Success ..You\'ve Added ..<b class="info">N{new_xpenses.cost}</b>.. Spent  Today!!',
            'flash':'alert-success',
            'link': f''})
    
    #if "rangeform" in request.form and rangeform.validate_on_submit(): #same-as-post-request\
    if rangeform.validate_on_submit(): #same-as-post-request\
        start = datetime.strptime(str(rangeform.start.data), '%Y-%m-%d').date() 
        end = datetime.strptime(str(rangeform.end.data), '%Y-%m-%d').date() 
        if end < start:
            start, end = end, start
        dept = rangeform.dept.data

        # Build the filters incrementally
        filters = [ and_( func.date(Expenses.created) == start) if start == end else \
            and_(Expenses.created >= start, Expenses.created <= end), Expenses.deleted==False,]
        if dept:
            filters.append(Expenses.dept == dept)
        #xps = Expenses.query.filter(and_(*filters)).all()
        xps = Expenses.query.filter(*filters).all()

        s_total =  db.session.query(func.sum(Sales.total) ).filter(func.Date(Sales.created) >= start, func.Date(Sales.created), Sales.deleted == False ).scalar()

        s_total = 0 if s_total == None else s_total

        if (xps == None) or not xps:
            return jsonify({ 
            'response': f'Hey!! Expense Not Found/Recorded Between ({start} to {end})',
            'flash':'alert-warning',
            'link': f'{url_for("main.kitchen_report")}'})
        
        x_total = sum([c.cost for c in xps ]) 
        xps_count = len(xps) #from-db-count
        report_id = (randint(0, 999999))
        #
        est_profit = int(s_total - x_total or 0)

        x_items = [{ 
                'comment':  x.comment,
                'dept': x.dept,
                'cost':  x.cost,
                'created':  x.created.strftime("%c")
            } for x in xps ]  , x_total, report_id, [start.strftime("%b"), end.strftime("%b")], s_total, est_profit, xps_count 
        return jsonify(x_items)

@endpoint.route('/x-categories', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<string:action>/x-categories', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def cate_action(item_id=None, action=None):
    cateform = CateForm()

    referrer =  request.headers.get('Referer')
    action, item_id,  = request.args.get('action', action ) , request.args.get('item_id', item_id )
    cate = Category.query.filter( or_(Category.id == item_id, Category.id == cateform.item_id.data), Category.deleted == False ).first()
    
    if request.method == 'DELETE' and cate != None and action == 'del':
        cate.deleted = True
        db.session.commit()
        flash(f'Success {cate.name} Deleted!', 'danger')
        return jsonify({ 
            'response': f'Hey!! You\'ve deleted this category {cate.name} today {cate.created}',
            'flash':'alert-danger',
            'link': f'{referrer}'})

    if cateform.validate_on_submit(): #same-as-post-request
    
        if item_id or cateform.item_id.data: 
            cate.name = cateform.name.data
            cate.dept = cateform.dept.data
            db.session.commit()
            flash(f'Success {cate.name} updated!', 'success')
            return jsonify({ 
                'response': f'Success {cate.name} updated!',
                'flash':'alert-success',
                'link': f'{referrer}'})

        new_cate = Category( 
            name = cateform.name.data,
            dept=cateform.dept.data, 
            )
        db.session.add(new_cate)
        db.session.commit()
        db.session.flush()
        db.session.refresh(new_cate) #refresh so-i-can-get-the-last/new-insert-id
        flash(f'Success {new_cate.name} Added!', 'success')
        return jsonify( { 
            'response': f'Success ..You\'ve Added ..<b class="info">{new_cate.name}</b>.. New Category Today!!',
            'flash':'alert-success',
            'link': f''})
    
    return jsonify({ 
        'response': f'Sorry, Something went wrong in your request ..<b class="info">{cateform.errors}</b>.. !!',
        'flash':'alert-success',
        'link': f''})

@endpoint.route('/history', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<int:history_id>/<string:action>/history', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def history_action(item_id=None, history_id=None, action=None):
    salesform = SalesForm()
    referrer =  request.headers.get('Referer') 
    
    action = request.args.get('action', action) 
    item_id  = request.args.get('item_id', item_id)  or salesform.item_id.data
    history_id  =  request.args.get('history_id', history_id)  or (salesform.history_id.data if 'history_id' in request.form else None)

    it = db.session.query(StockHistory).filter(
        and_(
            StockHistory.id == history_id, StockHistory.deleted == False,
            or_(
                StockHistory.item_id.isnot(None),
                StockHistory.apportion_id.isnot(None)
            )
        )
    ).first()


    #if request.method == 'DELETE' and it != None and action == 'del':
    #if request.method == 'DELETE' and it and action == 'del':
    if request.method == 'DELETE' and it and action == 'del':
        # it.deleted = True
        db.session.delete(it)
        db.session.commit()
        db.session.flush()
        #db.session.refresh()
        item_name = it.item.name if it.item else it.apportioned_item.items_title
        flash(f'Success, {item_name} Deleted!', 'danger')
        return jsonify({ 
            'response': f'Hey!! you\'ve deleted history for {item_name}',
            'flash':'alert-danger',
            'link': referrer
            })
    
    #print(it, history_id, item_id )

    return jsonify({ 
        'response': f'Hey stop!!!. This backup might be missing already',
        'flash':'alert-danger',
        'link': referrer})
    
@endpoint.route('/get_notifications/api', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def get_notifications():

    unread_notifications = Notification.query.filter(Notification.deleted == False).order_by(Notification.created.desc()).all()

    # Mark the fetched notifications as read
    for notification in unread_notifications:
        notification.is_read = True
    db.session.commit()

    # Return unread notifications as JSON
    notifications_data = [{'id': n.id, 'title': n.title, 'message': n.message, 'photo': n.photo, 'created': n.created.strftime('%H:%M:%S')} for n in unread_notifications]
    return jsonify(notifications=notifications_data)
    