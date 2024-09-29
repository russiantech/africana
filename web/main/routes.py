
from flask import g, render_template, stream_template, Blueprint, flash, request, jsonify
from flask_login import current_user, login_required
from sqlalchemy import and_
from  sqlalchemy.sql.expression import func
from web.utils.db_session_management import db_session_management
#from web.utils.calc_percent import cal_percent
from web.main.forms import (
    CateForm, ExpensesForm, StockForm, SalesForm, RangeForm, kitchen_cate_choice, cocktail_cate_choice, expense_choice
)
from web.models import (
    User, Expenses, Item, ApportionedItems, StockHistory, Cate, Sales
)
from web import calc_percent, db, Brand

from calendar import month_abbr

from web.utils.decorators import role_required
import traceback

main = Blueprint('main', __name__)

@main.route("/welcome")
@db_session_management
def welcome():
    try:
        context = {'pname': 'Enjoy in a natural way'} 
        return stream_template('welcome.html', **context )
    except Exception as e:
        error_message = str(e)
        traceback_info = traceback.format_exc()  # Get traceback information
        print( f"oops: {error_message}<br><pre>{traceback_info}</pre>")

@main.route("/")
@main.route("/home")
@login_required
@role_required('manager', 'admin')
@db_session_management
def index():

    month_short = month_abbr[1:]
    cate = Cate.query.filter_by(deleted=False).order_by(Cate.id).all()
    cate = [{'id': c.id, 'parent': c.parent, 'name': c.name, 'lev': c.lev} for c in cate]

    # Calculate total sales for each department using item.s_price
    kq = db.session.query(
        func.count(Sales.id).label('count'),
        func.sum(Sales.qty * Item.s_price).label('sales')
    ).join(Item, Item.id == Sales.item_id).filter(
        Sales.dept == 'k', Sales.deleted == False
    ).all()

    cq = db.session.query(
        func.count(Sales.id).label('count'),
        func.sum(Sales.qty * Item.s_price).label('sales')
    ).join(Item, Item.id == Sales.item_id).filter(
        Sales.dept == 'c', Sales.deleted == False
    ).all()

    bq = db.session.query(
        func.count(Sales.id).label('count'),
        func.sum(Sales.qty * Item.s_price).label('sales')
    ).join(Item, Item.id == Sales.item_id).filter(
        Sales.dept == 'b', Sales.deleted == False
    ).all()

    xp = db.session.query(func.sum(Expenses.cost).label('xps')).filter(Expenses.deleted == False).all()
    
    # Calculate total sales across all departments using item.s_price
    ts = db.session.query(func.sum(Sales.qty * Item.s_price).label("mysum")).join(Item, Item.id == Sales.item_id).filter(
        Sales.deleted == False
    ).all()

    bestselling = db.session.query(Item.name, func.sum(Sales.qty).label('t_qty')).join(Sales, Item.id == Sales.item_id).filter(
        Sales.deleted == False
    ).group_by(Item.id).order_by(func.sum(Sales.qty).desc()).limit(10).all()

    topselling = db.session.query(Item.name, func.sum(Sales.qty * Item.s_price).label('total')).join(
        Sales, Item.id == Sales.item_id
    ).filter(Sales.deleted == False).group_by(Item.id).order_by(func.sum(Sales.qty * Item.s_price).desc()).limit(2)

    k_count = [{'count': k.count, 'sales': k.sales} for k in kq]
    c_count = [{'count': k.count, 'sales': k.sales} for k in cq]
    b_count = [{'count': k.count, 'sales': k.sales} for k in bq]

    for (x, y) in zip(k_count, ts):
        k_percent = calc_percent.cal_percent(x['sales'], y[0])

    for (x, y) in zip(c_count, ts):
        c_percent = calc_percent.cal_percent(x['sales'], y[0])

    for (x, y) in zip(b_count, ts):
        b_percent = calc_percent.cal_percent(x['sales'], y[0])

    for (sl, xp) in zip(ts, xp):
        ts = sl[0]
        xp = xp[0]
        income = (ts - xp) if ts is not None and xp is not None else 0
    
    context = {
        'ts': ts or 0, 'xp': xp or 0, 'income': income or 0,
        'k_count': k_count, 'c_count': c_count, 'b_count': b_count,
        'k_percent': k_percent or 0,
        'c_percent': c_percent or 0,
        'b_percent': b_percent or 0,
        'bestselling': bestselling, 'topselling': topselling,
        'cate': cate, 'months': month_short}

    return stream_template('index.html', **context)

@main.route("/kitchen")
@login_required
@role_required('manager', 'admin', 'kitchen')
@db_session_management
def kitchen():

    form =  StockForm()
    items = Item.query.filter(Item.deleted == 0, Item.dept=='k').order_by( Item.created.desc() ).limit(70)
    categories = Cate.query.filter(Cate.deleted == 0, Cate.dept=='k').order_by( Cate.created.desc() ).limit(70)
    form.cate.choices = [ (cate.id, cate.name) for cate in categories]
    total_stock_value = sum(x.in_stock * x.s_price for x in items if x.dept == 'k')
    context = {
    'form' : form,
    'pname' : 'Africana Kitchen',
    'cate' : [('', 'Select a category')] + form.cate.choices,
    'items' : items,
    'total_stock_value': total_stock_value,
    }
    context['form'].dept.data = 'k'
    return stream_template('kitchen/index.html', **context)
 
@main.route("/kitchen-sales")
@login_required
@role_required('manager', 'admin', 'kitchen')
@db_session_management
def kitchen_sales():

    context = {
    'form' : SalesForm(),
    'pname' : 'Kitchen Sales',
    'items' : Item.query.filter(Item.deleted == 0, Item.dept=='k').order_by( Item.created.desc() ).limit(70),
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='k').order_by(Sales.created.desc()).limit(80),
    }
    context['form'].dept.data ='k'
    
    return stream_template('sales/kitchen.html', **context)

@main.route("/kitchen-report")
@login_required
@role_required('manager', 'admin', 'kitchen')
@db_session_management
def kitchen_report():
    context = {
    'form' : RangeForm(),
    'pname' : 'Kitchen Sales Report',
    'cate' : kitchen_cate_choice,
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='k').order_by(Sales.created.desc()).all(),
    } 
    context['form'].dept.data = 'k'
    return render_template('salesreport/kitchen.html', **context)

########************COCK-TAILS***********************##################
@main.route("/cocktail")
@login_required
@role_required('manager', 'admin', 'cocktail')
@db_session_management
def cocktail():
    
    form =  StockForm()
    items = Item.query.filter(Item.deleted == 0, Item.dept=='c').order_by( Item.created.desc() ).limit(70)
    categories = Cate.query.filter(Cate.deleted == 0, Cate.dept=='c').order_by( Cate.created.desc() ).limit(70)
    form.cate.choices = [ (cate.id, cate.name) for cate in categories]
    total_stock_value = sum(x.in_stock * x.s_price for x in items if x.dept == 'c')
    context = {
    'form' : form,
    'pname' : 'Cock Tail Department',
    'cate' : [('', 'Select a category')] + form.cate.choices,
    'items' : items,
    'total_stock_value': total_stock_value,
    }
    context['form'].dept.data = 'c'
    return stream_template('cocktail/index.html', **context)
    
@main.route("/cocktail-sales")
@login_required
@role_required('manager', 'admin','cocktail')
@db_session_management
def cocktail_sales():

    form =  SalesForm()
    form.dept.data ='c'
    context = {
    'form' : form,
    'pname' : 'Cocktail Sales',
    'items' : Item.query.filter(Item.deleted == 0, Item.dept=='c').order_by( Item.created.desc() ).limit(800),
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='c').order_by(Sales.created.desc()).limit(1000),
    }
    return stream_template('sales/cocktail.html', **context)
  
@main.route("/cocktail-report")
@login_required
@role_required('manager', 'admin', 'cocktail')
@db_session_management
def cocktail_report():
    context = {
    'form' : RangeForm(),
    'pname' : 'Cocktail Sales Report',
    'cate' : cocktail_cate_choice,
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='c').order_by(Sales.created.desc()).all(),
    } 
    context['form'].dept.data = 'c'
    return render_template('salesreport/cocktail.html', **context)
    
#***************************BAR & BEAR ***************************###########
@main.route("/bar")
@login_required
@role_required('manager', 'admin',  'bar')
@db_session_management
def bar():

    form =  StockForm()
    items = Item.query.filter(Item.deleted == 0, Item.dept=='b').order_by( Item.created.desc() ).limit(300)
    categories = Cate.query.filter(Cate.deleted == 0, Cate.dept=='b').order_by( Cate.created.desc() ).limit(800)
    form.cate.choices = [ (cate.id, cate.name) for cate in categories]
    total_stock_value = sum(x.in_stock * x.s_price for x in items if x.dept == 'b')
    context = {
    'form' : form,
    'pname' : 'Bar & Beer',
    'cate' : [('', 'Select a category')] + form.cate.choices,
    'items' : items,
    'total_stock_value': total_stock_value,
    }
    context['form'].dept.data = 'b'
    return stream_template('bar/index.html', **context)

@main.route("/bar-sales")
@login_required
@role_required('manager', 'admin','bar')
@db_session_management
def bar_sales():
    form =  SalesForm()
    form.dept.data ='b'
    context = {
    'form' : form,
    'pname' : 'Bar & Beer Sales',
    'items' : Item.query.filter(Item.deleted == 0, Item.dept=='b').order_by( Item.created.desc() ).limit(800),
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='b').order_by(Sales.created.desc()).limit(100),
    }
    return stream_template('sales/bar.html', **context)

@main.route("/bar-report")
@login_required
@role_required('manager', 'admin', 'bar')
@db_session_management
def bar_report():
    context = {
    'form' : RangeForm(),
    'pname' : 'Bar & Beer Sales Report',
    #'cate' : cocktail_cate_choice,
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='b').order_by(Sales.created.desc()).all(),
    } 
    context['form'].dept.data = 'b'
    return render_template('salesreport/bar.html', **context)

#*****************STOCK HISTORY***********************###########
@main.route("/stock-history")
@login_required
@role_required('*')
@db_session_management
def stock_history():
    context = {
    'form' : RangeForm(),
    'pname' : 'Product History',
    'cate' : cocktail_cate_choice, 
    'history' : StockHistory.query.filter(StockHistory.deleted == False).order_by(StockHistory.created.desc()).all(),
    } 

    bar_previous_total = sum(x.in_stock * x.item.s_price for x in context['history'] if x.item and x.item.dept == 'b')
    kitchen_previous_total = sum(x.in_stock * x.item.s_price for x in context['history'] if x.item and x.item.dept == 'k')
    cocktail_previous_total = sum(x.in_stock * x.item.s_price for x in context['history'] if x.item and x.item.dept == 'c')

    # Add kitchen_previous_total to the context dictionary
    context['bar_previous_total'] = bar_previous_total
    context['kitchen_previous_total'] = kitchen_previous_total
    context['cocktail_previous_total'] = cocktail_previous_total
    
    return render_template('stockhistory/stockhistory.html', **context)

@main.route("/apportioned-products")
@login_required
@role_required('*')
@db_session_management
def apportioned():        
    context = {
    #'get_corresponding_dept' : get_corresponding_dept,
    'form' : RangeForm(),
    'pname' : 'Apportioned Products',
    'apportioned' : ApportionedItems.query.filter(ApportionedItems.deleted == False).order_by(ApportionedItems.created.desc()).all(),
    #'apportoned_history' : StockHistory.query.filter(StockHistory.deleted == False, StockHistory.apportioned_id != None).order_by(StockHistory.created.desc()).all(),
    # Query ApportionedItems and join with StockHistory
    #'apportion_history':  ApportionedItems.query.outerjoin(StockHistory, ApportionedItems.id == StockHistory.apportioned_item_id).all()
    #'apportion_history':  ( db.session.query(apportioned, history).filter(apportioned.id == history.apportioned_item_id).all() )
    'apportion_history':  ( 
        db.session.query(ApportionedItems, StockHistory).filter(
        ApportionedItems.id == StockHistory.apportioned_item_id, and_(
            StockHistory.deleted == False, ApportionedItems.deleted == False,)
                ).order_by(StockHistory.created.desc()).all() )
    
    }
    return render_template('apportioned/index.html', **context)

@main.route("/expenses")
@login_required
@role_required('*')
@db_session_management
def expenses():
    context = {
    'xpenseform' : ExpensesForm(), #or SalesForm(),
    'rangeform' : RangeForm(), #or SalesForm(),
    'pname' : 'Expenses',
    'cate' : expense_choice,
    'sales' : Sales.query.filter(Sales.deleted == 0, Sales.dept=='k').order_by(Sales.created.desc()).all(),
    'xpenses' : Expenses.query.filter(Expenses.deleted == 0).order_by(Expenses.created.desc()).all(),
    } 
    return render_template('expenses/index.html', **context)

@main.route("/categories")
@login_required
@role_required('*')
@db_session_management
def cate():
    form =  CateForm()
    #categories = Cate.query.filter(Cate.deleted == 0, Cate.dept=='k').order_by( Cate.created.desc() ).limit(70)
    categories = Cate.query.filter(Cate.deleted == 0).order_by( Cate.created.desc() ).limit(70)

    form.dept.choices = [ ('', 'choose'), ('k', 'Kitchen'), ('c', 'Cocktail'), ('b', 'Bar')]

    context = {
    'form' : form,
    'pname' : 'Africana Categories',
    'cate' : categories,
    }
    return stream_template('cate/index.html', **context)

@main.route("/people", methods=['GET', 'POST'])
@login_required
@role_required('*')
@db_session_management
def people():

    referrer =  request.headers.get('Referer')
    
    username, action = request.args.get('username', None), request.args.get('action', None)
    if username != None and action == 'del':
        if not current_user.is_admin():
            return jsonify({ 
                'response': f'Hey! {current_user.name or current_user.username}, You do not have permission to remove or delete this account',
                'flash':'alert-danger',
                'link': f'{referrer}'})

        user = User.query.filter(User.deleted == 0, User.username==username).first()
        
        if user:
            user.name = user.name
            user.deleted = True
            db.session.commit()
            
            flash(f'User Has Been Deleted!', 'danger')
            return jsonify({ 
                'response': f'Hmm, User Deleted!!!',
                'flash':'alert-danger',
                'link': f'{referrer}'})
        return jsonify({ 
                'response': f'User Not Available',
                'flash':'alert-warning',
                'link': f'{referrer}'})
    
    page = request.args.get('page', 1, type=int)  # Get the requested page number
    per_page = 10  # Number of items per page
    #users = User.query.order_by(User.id.desc()).paginate(page=page, per_page=per_page)
    users = User.query.filter(User.deleted == 0).order_by( User.created.desc()).paginate(page=page, per_page=per_page)
    g.brand = Brand.query.first()
    g.user = User.query.filter(User.deleted == 0, User.username==username).first()
    context = {
    'pname' : 'People : (Staffs) (Customers) (Suppliers)',
    'users': users
    }
    #return stream_template('people/index.html', **context)
    return render_template('people/index.html', **context)

#***************************************************

@main.route('/us')
@login_required
@db_session_management
def us():
    return render_template("us.html", pname='About Us')

@main.route('/intouch')
@login_required
@db_session_management
def intouch():
    return render_template("intouch.html", pname='Reach Us')

@main.route('/terms')
@login_required
@db_session_management
def terms():
    return render_template("terms.html", pname='Terms Of Use')

@main.route('/privacy')
@login_required
@db_session_management
def privacy():
    return render_template("privacy.html", pname='Privacy Policy')

@main.route('/faqs')
@login_required
@db_session_management
def faqs():
    return render_template("faqs.html", pname='Frequently Asked Questions')

@main.route('/testify')
@login_required
@db_session_management
def testify():
    return render_template("testify.html", pname='Testimonials')


