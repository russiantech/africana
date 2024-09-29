from flask_wtf import FlaskForm

from datetime import datetime
from wtforms import StringField, FileField, TextAreaField, SubmitField, SelectField, \
    IntegerField, HiddenField, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, Email
from flask_wtf.file import FileField, FileAllowed

state_choice = [('','choose'), ('ls','Lagos'), ('abj','Abuja'), ('ph','Portharcourt'),  ('abia','Abia '), ('cr','Cross River') ]
country_choice = [('','Choose'), ('ng','Nigeria'), ('gh','Ghana'), ('cam','Cameroun'),  ('tg','Togo '), ('us','United States') ]
payOptionChoice = [('fw','Flutterwave'), ('ps','Paystack'), ('pp','Paypal'), ('card','Card payment'),  ('cash','Cash on delivery'), ('chq','Cheque payment') ]

size_choice = [('s','S'), ('m','M'), ('l','L'), ('xl','XL'),  ('xxl','XXL')]
color_choice = [('#ff6191',''), ('#33317d',''), ('#56d4b7',''), ('#009688','')]
cate_choice = {                                                                                                                
        #'feline': {'second-nested' : [(3, 'cat'), (5, 'lion')] },                                                                                   
        'services': [(4, 'dog')],       
        'realtors': [(3, 'cat'), (5, 'lion')],                                                                                   
        'lekki-zone': [(4, 'dog')],                   
        'feline2': [(3, 'cat'), (5, 'lion')],                                                                                                                                                                                   
        }
 
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

class PostForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    desc = TextAreaField('Describe this listing', validators=[Length(min=0, max=300)])
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
