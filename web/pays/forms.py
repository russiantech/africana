from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField


from datetime import datetime
from flask import request
from wtforms import StringField, TextAreaField, SubmitField, DateField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from web.models import User

state_choice = [('','Which State'), ('lagos','Lagos'), ('abuja','Abuja'), ('portharcourt','Portharcourt'),  ('abia','Abia '), ('cross-river','Cross River') ]

this_month = datetime.now().strftime('%m')
this_year = datetime.now().strftime('%y') #without-century
current_year_full = datetime.now().strftime('%Y')  # 2023
current_year_short = datetime.now().strftime('%y')  # 10 without century


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

    """ def validate_username(self, username):
        #if ( (current_user.is_admin()) | (current_user.username == usr.username) ):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.username.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} Is Not Allowed In Username.") 
            
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(f'That username `{username.data}` is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            
    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That phone number belongs to a different account. Please choose a different one.') """