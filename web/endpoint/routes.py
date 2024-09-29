from calendar import month_abbr
from datetime import datetime
from decimal import Decimal
from random import randint
from flask import jsonify, Blueprint, request, url_for, flash
from flask_login import current_user, login_required

from sqlalchemy import and_, or_
from sqlalchemy.sql import func, extract

from web import db
from web.main.forms import CateForm, ExpensesForm, StockForm, SalesForm, RangeForm

from web.models import Cate, Expenses, Item, ApportionedItems, StockHistory, Notification, Sales
from web.utils.ip_adrs import user_ip
from web.utils.sequence_int import generator
from web.utils.db_session_management import db_session_management

endpoint = Blueprint('endpoint', __name__)
def exclude_deleted(query):
    return query.filter_by(deleted=False)

@endpoint.route('/new-stock', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<string:action>/new-stock', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def stock_action(item_id=None, action=None):
    stockform = StockForm()
    action, item_id,  = request.args.get('action', action ) , request.args.get('item_id', item_id )
    it = exclude_deleted(Item.query.filter( (Item.id == item_id) | (Item.id == stockform.item_id.data)) ).first()

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
            'response': f'invalid { stockform.errors, stockform.cate.data}  </b>..',
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
            it.deleted = False #This would ensure unique constraints defined under Item() model also works by excluding the deleted columns

            db.session.add(saved_history)
            db.session.commit()
            db.session.flush()
            db.session.refresh(saved_history) #refresh so-i-can-get-the-last/new-insert-id
            
            #flash(f'Success {it.name} updated!', 'success')
            return jsonify({ 
                'response': f'Success {it.name} updated!',
                'flash':'alert-success',
                'link': f'{referrer}'})
        

        saved_stock = Item(
            user_id = current_user.id if current_user.is_authenticated else 0, #so that even-if you're not logged in, you can still place orders
            #cate = selected_cate,
            cate = stockform.cate.data,
            name=stockform.name.data, 
            in_stock=stockform.in_stock.data or 0, 
            new_stock=stockform.new_stock.data if 'new_stock' in request.form else 0, #on-my-latest-updates-this-field-is-ignored
            c_price=stockform.c_price.data if 'c_price' in request.form else 0, 
            s_price=stockform.s_price.data, 
            dept=stockform.dept.data if 'dept' in request.form else 'k', 
            ip = user_ip(),
            deleted = False #This would ensure unique constraints defined under Item() model also works by excluding the deleted columns

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
    
    
@endpoint.route('/sales', methods=['POST','PUT', 'DELETE', 'GET']) 
@endpoint.route('/<int:item_id>/<int:sales_id>/<string:action>/sales', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def sales_action(item_id=None, sales_id=None, action=None):

    salesform = SalesForm()
    rangeform = RangeForm()
    referrer =  request.headers.get('Referer') 
    
    action = request.args.get('action', action) 
    item_id  = request.args.get('item_id', item_id)  or salesform.item_id.data
    sales_id  =  request.args.get('sales_id', sales_id)  or (salesform.sales_id.data if 'sales_id' in request.form else None)

    it = db.session.query(Sales).join(Item, Sales.item_id==Item.id).filter( and_(Sales.id == sales_id, Sales.deleted == False) ).first()
    #it = db.session.query(Sales).join(Item, Sales.item_id==Item.id).filter( and_(Sales.id == item_id, Sales.deleted == False) ).first()
    instock = Item.query.filter(Item.id == item_id, Item.deleted == False).first() #check-stock-balance-b4-adding-sales
    #return str(salesform.data)
    if request.method == 'DELETE' and it != None and action == 'del':
        it.deleted = True
        db.session.commit()
        db.session.flush()
        #db.session.refresh()
        flash(f'Success, {it.salez.name} Deleted!', 'danger')
        return jsonify({ 
            'response': f'Hey!! you\'ve deleted {it.salez.name}',
            'flash':'alert-danger',
            'link': f'{referrer}'})
    
    if request.method == 'POST':
        #submit = form.year.data if 'year' in request.form  else None, #str
        #print(request.form) #//DEBUGGING
        #if "pcs_sold" or 'pcs_left' in request.form:
        if "pcs_sold" in request.form or 'pcs_left' in request.form:
            
            pcs_sold =int(salesform.pcs_sold.data) if salesform.pcs_sold.data is not None else None
            pcs_left =int(salesform.pcs_left.data) if salesform.pcs_left.data is not None else None
                
            #if not salesform.item_id.data or not salesform.pcs_sold.data or int(salesform.item_id.data) <= 0 or int(salesform.pcs_sold.data) <= 0:
            if not salesform.item_id.data or pcs_left == None or int(salesform.item_id.data) <= 0 :
                return jsonify({ 
                    'response': f"Ensure a product is selected & either closing-stock or quantity sold is also provided!",
                    'flash': 'alert-warning',
                    'link': referrer
                })
            
            if salesform.validate_on_submit(): #same-as-post-request
                #B4 adding/updating, confirm there's enough stock balance
                if instock == None:
                    return jsonify({ 
                        'response': f'Hey bro, Seems The Product Is\'nt Available Right Now !',
                        'flash':'alert-warning',
                        'link': f'{referrer}'})
                
                # Check if there are associated ApportionedItems
                apportioned_items = instock.apportioned_quantities
                if apportioned_items:
                    for apportioned_item in apportioned_items:
                        available_qty = apportioned_item.items_qty
                        print(f"Apportioned Item ID: {apportioned_item.id}, Items Quantity: {available_qty}")
                    else:
                        print(f"Item ID: {instock.id} has no associated Apportioned Items")
                else:
                    available_qty = instock.in_stock
                
                #calculate qty based on closing-stock(pcs_left) prior to direct pcs_sold
                #pcs_left = int(salesform.pcs_left.data)
                #pcs_left =int(salesform.pcs_left.data) if salesform.pcs_left.data is not None else None
                

                #if 'pcs_left' in request.form and pcs_left > 0 :
                #if pcs_left is not None and pcs_left >= 0 :
                if pcs_left is not None and pcs_left <= 0 :
                    qty_sold = int(available_qty)
                    
                #elif pcs_left is not None and pcs_left == available_qty :
                #    qty_sold = 0
                    
                elif pcs_left is not None and pcs_left < available_qty :
                    qty_sold = int(available_qty - pcs_left)
                
                elif pcs_left is not None and pcs_left > available_qty :
                    return jsonify({ 
                        'response': f'Your closing stock of {pcs_left} is more than current stock of {available_qty}, indicating that you probably got new stock but did not add it to your record',
                        'flash':'alert-warning',
                        'link': f'{referrer}'})
                        
                elif pcs_left is not None and pcs_left == available_qty :
                    return jsonify({ 
                        'response': f'Your closing stock of {pcs_left} is same as current stock of {available_qty}, indicating no sales or you probably did not update your stock record.',
                        'flash':'alert-warning',
                        'link': f'{referrer}'})
                        
                else:
                    #qty_sold = int(salesform.pcs_sold.data)
                    qty_sold = pcs_sold
                    #print(pcs_sold, qty_sold)
                
                if qty_sold == None:
                    return jsonify({ 
                        'response': f'Kindly provide either a closing-stock or quantity-sold to track & record this sales.',
                        'flash':'alert-warning',
                        'link': f'{referrer}'})
                        
                if qty_sold == 0:
                    return jsonify({ 
                        'response': f'Could not record sales probably because there nothing in stock, the current stock level is {available_qty}',
                        'flash':'alert-warning',
                        'link': f'{referrer}'})
                        
                
                #if (instock.in_stock < salesform.pcs_sold.data):
                #if (available_qty < qty_sold) or (available_qty < pcs_left):
                if (qty_sold is not None and available_qty < qty_sold) or (pcs_left is not None and available_qty < pcs_left):
                    """ 
                    When calculating sales using the closing stock method (Quantity Sold = Initial Stock - Closing Stock), the closing stock should ideally be less than or equal to the 
                    available initial stock. If the closing stock is greater than the available initial stock, it may lead to negative quantities sold or other inconsistencies.
                    Here's the logic breakdown:
                    Closing Stock <= Initial Stock:
                        This is the expected scenario. Closing stock represents the stock remaining after sales, and it should not exceed the available initial stock. 
                        If it does, it suggests a potential issue with the data.
                    Closing Stock > Initial Stock:
                        This scenario is unusual and may indicate a problem with data entry or calculation. If the closing stock is greater than the initial stock, 
                        it implies that more stock is available after sales than was initially present, which is not logical.
                        Therefore, when using the closing stock method to calculate sales, it's generally a good practice to validate and ensure that:
                    Closing Stock is Reasonable:
                        Closing stock values are reasonable and do not exceed the initial stock.
                    Error Handling:
                        Implement error handling and validation checks to catch scenarios where closing stock is greater than initial stock. 
                    """

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
                        'response': f"You only have {available_qty} of {instock.name} left. Update records first, \
                            you're trying to record {abs(qty_sold)} of qty sold which is more than what you have currently in stock.",
                        'flash':'alert-warning',
                        'link': f'{url_}' 
                        })

                #return f"{salesform.data, it, sales_id, salesform.sales_id.data  }"
                if (it and salesform.is_update.data == True):
                    #return f"{available_qty, qty_sold}"
                    it.salez.in_stock += it.qty #add-back-deducted-qty-when-sales-was-recorded if it's an update.
                    it.qty_left = pcs_left
                    it.qty = qty_sold #record-as-new-sales
                    it.salez.in_stock -= it.qty  #re-deduct the new-recorded sales
                    it.dept = salesform.dept.data 
                    it.ip = user_ip()
                    db.session.commit()
                    db.session.flush()
                    #flash(f'Success {it.salez.name} updated!', 'success')
                    return jsonify({ 
                        'response': f'Success!!!!, {it.salez.name} updated to {it.qty}  sold !',
                        'flash':'alert-info',
                        'link': ''})
                
                new_sales = Sales( 
                    item_id = item_id,
                    qty_left=pcs_left,
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

                #flash(f'Success africana, you\ve recorded {new_sales.qty} pieces of {new_sales.salez.name} sold !', 'success')
                return jsonify({ 
                    'response': f'Success africana, you have recorded {new_sales.qty} pieces of {new_sales.salez.name} sold !',
                    'flash':'alert-success',
                    'link': f''})
            
            return jsonify({ 
                'response': f'Some issues > {salesform.errors}  </b>..',
                #'response': f'invalid { salesform, salesform.errors, salesform.data}  </b>..',
                'flash':'alert-warning',
                'link': f''})
        
        elif ("start" or "end") in request.form:   
            if rangeform.validate_on_submit(): #same-as-post-request\
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
        else:
            return jsonify({ 
                    'response': f'Not Validated { salesform.data, rangeform.data}  </b>..',
                    'flash':'alert-warning',
                    'link': f''})

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
    cate = Cate.query.filter( or_(Cate.id == item_id, Cate.id == cateform.item_id.data), Cate.deleted == False ).first()
    
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

        new_cate = Cate( 
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
                StockHistory.apportioned_item_id.isnot(None)
            )
        )
    ).first()


    #if request.method == 'DELETE' and it != None and action == 'del':
    #if request.method == 'DELETE' and it and action == 'del':
    if request.method == 'DELETE' and it and action == 'del':
        it.deleted = True
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
    
@endpoint.route('/<string:dt>/api', methods=['POST', 'GET', 'PUT', 'DELETE']) 
@login_required
@db_session_management
def api(dt):
    
    current_year = datetime.now().year

    if dt == 'monthly_sales':

        monthly_sales = db.session.query(
            extract('month', Sales.updated).label('month'),
            func.sum(Sales.qty * Item.s_price).label('total_sales')
        ).join(Item, Item.id == Sales.item_id).filter(
            extract('year', Sales.updated) == current_year,
            Sales.deleted == False
        ).group_by(extract('month', Sales.updated)).all()

        monthly_sales = [{'monthabr': month_abbr[x.month], 'sales': x.total_sales} for x in monthly_sales]

        return jsonify(monthly_sales)

    if dt == 'monthly_xp':
        monthly_xp = db.session.query(
            extract('month', Expenses.updated).label('month'),
            func.sum(Expenses.cost).label('total_xp')
        ).filter(
            extract('year', Expenses.updated) == current_year,
            Expenses.deleted == False
        ).group_by(extract('month', Expenses.updated)).all()

        month_short = month_abbr[1:]

        monthly_xp = [{'monthabr': month_abbr[x.month], 'xps': x.total_xp} for x in monthly_xp]

        return jsonify(monthly_xp)

    if dt == 'monthly_income':
        monthly_income = []
        for year, month in db.session.query(func.extract('year', Sales.updated), func.extract('month', Sales.updated)).distinct():
            sales_amount = db.session.query(func.sum(Sales.qty * Item.s_price)).join(Item, Item.id == Sales.item_id).filter(
                func.extract('year', Sales.updated) == year,
                func.extract('month', Sales.updated) == month,
                Sales.deleted == False
            ).scalar() or 0.0
            expenses_amount = db.session.query(func.sum(Expenses.cost)).filter(
                func.extract('year', Expenses.updated) == year,
                func.extract('month', Expenses.updated) == month,
                Expenses.deleted == False
            ).scalar() or 0.0
            income = Decimal(sales_amount - expenses_amount) if (sales_amount and expenses_amount) is not None else 0
            monthly_income.append({'monthabr': month_abbr[month], 'income': income})

        return jsonify(monthly_income)

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
    