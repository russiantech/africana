from flask_wtf import FlaskForm

from datetime import datetime
from wtforms import StringField, FileField, SubmitField, SelectField, \
    IntegerField, HiddenField, BooleanField, SelectMultipleField, widgets, DateField, TextAreaField
#from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Optional, Length, Email
from flask_wtf.file import FileField, FileAllowed

from web.models import Items

state_choice = [('','choose'), ('ls','Lagos'), ('abj','Abuja'), ('ph','Portharcourt'),  ('abia','Abia '), ('cr','Cross River') ]
country_choice = [('','Choose'), ('ng','Nigeria'), ('gh','Ghana'), ('cam','Cameroun'),  ('tg','Togo '), ('us','United States') ]
payOptionChoice = [('fw','Flutterwave'), ('ps','Paystack'), ('pp','Paypal'), ('card','Card payment'),  ('cash','Cash on delivery'), ('chq','Cheque payment') ]

kitchen_cate_choice = [('','-'), ('1','Chicken'), ('2','Fish'), ('3','Skin & Beef'), ('4','Swallow & Soup'),  ('5','Noodles')]
cocktail_cate_choice = [('','-'), ('1','Flips and Nogs'), ('2','Hot Drinks'), ('3','Spirit-Forward Cocktails'), ('4','Sours'),  ('5','Ancestrals')]

size_choice = [('s','S'), ('m','M'), ('l','L'), ('xl','XL'),  ('xxl','XXL')]
color_choice = [('#ff6191',''), ('#33317d',''), ('#56d4b7',''), ('#009688','')]
cate_choice = {                                                                                                                
        #'feline': {'second-nested' : [(3, 'cat'), (5, 'lion')] },                                                                                   
        'services': [(4, 'dog')],       
        'realtors': [(3, 'cat'), (5, 'lion')],                                                                                   
        'lekki-zone': [(4, 'dog')],                   
        'feline2': [(3, 'cat'), (5, 'lion')],                                                                                                                                                                                   
        }

expense_choice = [('','Select Expense Department'), ('k','Kitchen'), ('c','Cocktail'), ('b','Bar')]
dept_choice = [('','Select Department'), ('k','Kitchen'), ('c','Cocktail'), ('b','Bar')]

#this_day= datetime.now()
this_month = datetime.now().strftime('%m')
this_year = datetime.now().strftime('%y') #without-century
current_year_full = datetime.now().strftime('%Y')  # 2023
current_year_short = datetime.now().strftime('%y')  # 10 without century

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class MultiColorField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.Input('color')

# //currently not in use
class MultiImageField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.Input('file')
##############

class PayForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    amt = HiddenField('Amt', validators=[DataRequired()])
    submit = SubmitField('Authorize Payment')

class OrderInfoForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone',  validators=[ DataRequired(), Length(min=2, max=20)])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    state = SelectField('State', choices=state_choice)
    bustop = StringField('Nearest Bus Stop', validators=[DataRequired(), Length(min=2, max=20)])
    street = StringField('Street', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Place My Order Now')

class OrderForm(FlaskForm):
    email = StringField('Valid email address', validators=[DataRequired(), Email()])
    phone = StringField('Active phone number',  validators=[Length(min=2, max=20)])
    name = StringField('Name(s)', validators=[DataRequired(), Length(min=2, max=20)])
    adrs = StringField('Address', validators=[DataRequired(), Length(min=2, max=20)])
    country = SelectField('Country', choices=country_choice, validators=[DataRequired(), Length(min=2, max=20)])
    order_amt = IntegerField('Payment Total', validators=[DataRequired()])
    pment_option = SelectField('Payment Option', choices=payOptionChoice, validators=[DataRequired(), Length(min=2, max=20)])
    state = SelectField('State', choices=state_choice, validators=[DataRequired(), Length(min=2, max=20)])
    zipcode = StringField('Zipcode', validators=[DataRequired(), Length(min=5, max=10)])
    tnc = BooleanField('Terms & Conditions', validators=[DataRequired()])
    submit = SubmitField('Place My Order Now')

class StockForm(FlaskForm):
    photo = FileField('Photo', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    name = StringField('Name(s)', validators=[DataRequired(), Length(min=2, max=20)])
    cate = SelectField('Category', coerce=int, choices=[], validate_choice = False)
    dept = SelectField('Department', choices=dept_choice, validators=[DataRequired()])
    in_stock = StringField('Quantity', default=0)
    new_stock = IntegerField('New Stock', default=0, render_kw={"placeholder": "New Stock"})
    c_price = IntegerField('Cost Price', default=0)
    s_price = IntegerField('Selling Price', default=0)
    item_id = IntegerField('Item Id')
    submit = SubmitField('Save')

from wtforms.widgets import CheckboxInput
class ApportionForm(FlaskForm):
    items_title = StringField('Item Title', validators=[DataRequired()])
    items_dept = SelectField('Department', choices=dept_choice, validators=[DataRequired()])
    #items_qty = IntegerField('Quantity', default=0, validators=[DataRequired()])
    items_qty = StringField('Quantity')

    items_series = SelectMultipleField(
        'Select Products',
        widget=CheckboxInput(),
        #validators=[InputRequired("Please select at least one item you can sell from quantity apportioned.")]
    )
    def __init__(self, *args, **kwargs):
        super(ApportionForm, self).__init__(*args, **kwargs)
        # Fetch and set the choices dynamically from your database
        self.items_series.choices = [(str(item.id), str(item.name) ) for item in Items.query.all()]
        #self.item_series.choices = [(item.id, str(item.name) ) for item in Items.query.all()]
    submit = SubmitField('Save')

class SalesForm(FlaskForm):
    photo = FileField('Photo')
    sales_id = IntegerField('Sales-Id', validators=[Optional()])
    item_id = IntegerField('Pcs', validators=[DataRequired()]) #will-be-update-from-front-end, value-will be Item_id(fk to item-table)
    pcs_sold = IntegerField('Pcs Sold', validators=[Optional()])
    pcs_left = IntegerField('Pcs Left', validators=[Optional()])
    """ pcs_sold = IntegerField('Pcs Sold', validators=[DataRequired()])
    pcs_left = IntegerField('Pcs Left', validators=[DataRequired()]) """
    price = IntegerField('Price', validators=[Optional()])
    total = IntegerField('Total', validators=[Optional()])
    is_update = BooleanField('Is Update')
    dept = HiddenField('dept', validators=[DataRequired()])
    submit = SubmitField('Save')

class CateForm(FlaskForm):
    #photo = FileField('Photo', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    item_id = IntegerField('Category_id', default=0) #will-be-update-from-front-end, value-will be Item_id(fk to item-table)
    name = StringField('Name(s)', validators=[DataRequired(), Length(min=2, max=20)])
    dept = SelectField('dept', choices=[('', 'Select Department'), ('b', 'Bar'), ('k', 'Kitchen'), ('c', 'Cocktails')], validators=[DataRequired()])
    submit = SubmitField('Save')

class RangeForm(FlaskForm):
    start = DateField('Start', format='%Y-%m-%d', validators=[DataRequired()])
    end = DateField('end', format='%Y-%m-%d', validators=[DataRequired()])
    dept = SelectField('dept', choices=[('', 'Department'), ('k', 'Kitchen'), ('c', 'Cocktail'), ('b', 'Bar')])
    generate = SubmitField('Generate Report Now')

#cdate = datetime.strptime(str(datetime.now()), '%Y-%m-%d ').date() 
#cdate = datetime.now().date() 
#print(cdate)
class ExpensesForm(FlaskForm):
    item_id = IntegerField('Item id') #will-be-update-from-front-end, value-will be Item_id(fk to item-table)
    dept = SelectField('Select Department', choices=expense_choice, validators=[DataRequired()])
    #cate = SelectField('Category', choices=kitchen_cate_choice, validators=[DataRequired()])
    cost = IntegerField('Cost', validators=[DataRequired()])
    comment = TextAreaField('Descrption', validators=[DataRequired()]) #desc === comment in db
    created = DateField('end', format='%Y-%m-%d', default=(datetime.now()) )
    save = SubmitField('Save Expenses Now')

class PostForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    photo = FileField('photo', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    quant = IntegerField('Quantity')
    price = IntegerField('Price( In USD )', validators=[DataRequired()])
    size = MultiCheckboxField('Size(s)', choices=size_choice)
    color = MultiColorField('Color(s)', choices=color_choice)
    #cate = HiddenField('Category')
    #cate = SelectField('Category')
    cate = SelectMultipleField('Classify it', choices = cate_choice , widget=widgets.Select(multiple=False))

    ip = StringField('Zipcode', validators=[DataRequired(), Length(min=5, max=10)])
    tag = StringField('Product tags ( Type & make comma to separate tags )')

    #photos = MultiImageField('Photo(s),', validators=[DataRequired(), FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])

    photo = FileField('main photo,', validators=[DataRequired(), FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    photo0 = FileField('Thunb 01', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    photo1 = FileField('Thumb 02', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    photo2 = FileField('Thumb 03', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    photo3 = FileField('Thumb 04', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    photo4 = FileField('Thumb 05', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])
    photo5 = FileField('Thumb 06', validators=[FileAllowed(['webp', 'png', 'jpg', 'jpeg', 'gif'])])

    submit = SubmitField('Post My Listing')
