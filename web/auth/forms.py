
from flask_login import current_user
from wtforms.csrf.session import SessionCSRF
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from web.models import User, Role

level_choice = [('','Course Level'), ('novice','Novice'), ('beginner','Beginner'), ('expert','Expert'),  ('pro','Pro'), ('advanced','Advanced') ]
gender_choice = [('', 'Gender'), ('f', 'Female'), ('m', 'Male'), ('o', 'Other')]
lang_choice = [('', 'language'), ('english', 'english'), ('french', 'french'), ('spanish', 'spanish'), ('latin', 'latin'), ('pidgin', 'pidgin'), ('other', 'other')]
city_choice = [('', 'current city'), ('Lagos','Lagos'), ('Portharcourt','Portharcourt'), ('New York','New York'), ('Canada','Canada'), ('Calabar','Calabar'), ('Uyo','Uyo')]
role_choice = [('', 'Assign Role')]
#role_choice = [(r.name, r.name) for r in Role.query.all()]

bank_choice = [('', 'Bank'), ('fcmb','First City Monument Bank'), ('uba','United Bank Of Africa'), ('first bank','First Bank'), \
               ('opay','Opay'), ('union bank','Union Bank'), ('gtb','Quaranty Trust Bank'), ('ecobank','Eco bank'), ('access bank','Access Bank')]

def is_admin(user):
    return user.is_authenticated and 'admin' in user.roles

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=50)])
    tnc = BooleanField('Terms & Conditions', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        excluded_chars = " *?!'^+%&/()=}][{$#" #clean_ups
        for char in self.username.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} Is Not Allowed In Username.") 

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_phone(self, phone):
        excluded_chars = "~@*?!;$%`\":<>'^%&/()=}][{$#" #clean_ups
        for char in self.phone.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} Is Not Allowed In Phone Numbers.") 
            
            if len(phone.data) < 7:
                raise ValidationError(f" ({phone.data}) Is Not A Valid Phone Number.") 
            
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('That Phone Number is Already In Use. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
            

class SigninForm(FlaskForm):
    signin = StringField('Username, Email Or Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_me(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Invalid Login Details. Try')


class UpdateMeForm(FlaskForm):
    #poster = FileField('Add Course Poster Image', validators=[ DataRequired(), FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4'])])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'svg', 'webp', 'gif', 'jpeg', 'png'])])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username:', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Mobile Number',  validators=[ DataRequired(), Length(min=2, max=20)])
    password = StringField('Password:')
    repeat_password = StringField('Repeat Password:')
    acct_no = StringField('Account Number:',  validators=[DataRequired(),Length(min=10, max=10)])
    bank = SelectField('Bank:', choices=bank_choice, validators=[DataRequired(),] )
    city = SelectField('City', choices=city_choice)
    role = SelectField('User Role', coerce=int, choices=role_choice)
    cate = SelectField('User Category', choices=[('', 'Select'), ('staff', 'One of the staffs'), ('customer', 'Africana customer'), ('supplier', 'Africana Supplier(s)')])
    #role = SelectField('User Role', coerce=int, choices=role_choice, render_kw={'class': 'readonly-select', 'readonly': 'readonly' if g.is_admin() else None})
    #role = SelectField('User Role', coerce=int, choices=role_choice, default=current_user.role if current_user.is_authenticated else None)
    about = TextAreaField('About You')
    instagram = StringField('Instagram Url:')
    facebook = StringField('Facebook Url:')
    twitter = StringField('Twitter Url:')
    linkedin = StringField('Linkedin Url:')
    gender = SelectField('Gender', validators=[DataRequired()], choices=gender_choice)
    submit = SubmitField('Save Information(s)')

    """  def __init__(self, csrf_secret_key='your_default_csrf_secret_key', *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the default CSRF token value
        self.csrf_token = SessionCSRF() """

    # Exclude password field when using obj parameter / I comment the whole thing bcos of error  "Password must be non-empty."
    """ def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude', [])
        super(UpdateMeForm, self).__init__(*args, **kwargs)
        if 'password' in exclude_fields:
            self.password.data = ''  # Set password field data to empty """

    def load_role(self):
        self.role = Role.query.all()
        return self.role
            
    def validate_password(self, repeat_password):
        if self.password != repeat_password:
                raise ValidationError(f"Repeat Password Must Match Initial Password {repeat_password} ") 
            
    def validate_username(self, username):
        #if ( (current_user.is_admin()) | (current_user.username == usr.username) ):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.username.data:
            if char in excluded_chars:
                raise ValidationError(f"Character {char} Is Not Allowed In Username.") 
            
        if username.data != current_user.username and not current_user.is_admin():
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(f'That username `{username.data}` is taken. Please choose a different one.') 

    def validate_email(self, email):
        if email.data != current_user.email and not current_user.is_admin():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            
    def validate_phone(self, phone):
        if phone.data != current_user.phone and not current_user.is_admin():
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That phone number belongs to a different account. Please choose a different one.')


class ForgotForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(f'Email({email.data}) Not Recognized')


class ResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')