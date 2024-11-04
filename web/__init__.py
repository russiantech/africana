from datetime import datetime
from flask import (
    Flask
)
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_session import Session
# from flask_oauthlib.client import OAuth //deprecated
from web.models import User
from web.utils.helpers import categ, find_dept_by_name, calc_percent, is_active, slugify
from web.models import db
from calendar import month_abbr

from dotenv import load_dotenv
load_dotenv()

f_session = Session()
bcrypt = Bcrypt()
s_manager = LoginManager()
mail = Mail()
migrate = Migrate()
moment = Moment()

from authlib.integrations.flask_client import OAuth
oauth = OAuth()

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

s_manager.login_view = 'auth.signin'
@s_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#s_manager.login_view = 'auth.signin'

def configure_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    f_session.init_app(app)
    bcrypt.init_app(app)
    s_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    oauth.init_app(app)
    csrf.init_app(app)

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('confiq.py')  # Load configuration from a separate file
    #db = SQLAlchemy(app)
    #s_manager = LoginManager(app)
    configure_extensions(app)
    
    app.config['WTF_CSRF_ENABLED'] = False # disable csrf

    # Register blueprints
    from web.auth.routes import auth
    # from web.account.routes import acct
    from web.main.routes import main
    from web.pays.routes import pay
    from web.endpoint.routes import endpoint
    # from web.endpoint.apportion import apportion
    from web.errors.handlers import errors

    app.register_blueprint(auth)
    # app.register_blueprint(acct)
    app.register_blueprint(main)
    app.register_blueprint(pay)
    app.register_blueprint(endpoint)
    # app.register_blueprint(apportion, url_prefix='/api')
    app.register_blueprint(errors)

    from web.apis.apportion import apportion_items_bp
    app.register_blueprint(apportion_items_bp, url_prefix='/api')
    
    from web.apis.stats import stats_bp
    app.register_blueprint(stats_bp, url_prefix="/api")
    
    # from web.apis.sales_bak_0 import sales_bp
    from web.apis.sales import sales_bp
    app.register_blueprint(sales_bp, url_prefix="/api")
    
    from web.apis.items import items_bp
    app.register_blueprint(items_bp, url_prefix="/api")
    
    # Other configuration and app setup
    app.jinja_env.filters['slugify'] = slugify
    # Other configuration and app setup
    app.jinja_env.filters['categ'] = categ
    app.jinja_env.filters['find_dept_by_name'] = find_dept_by_name
    app.jinja_env.globals.update(is_active=is_active)

    # Context processor for common data
    @app.context_processor
    def inject_common_data():
        now = datetime.utcnow()
        return {
            'now': now,
            'cyear': now.year % 100,
            'percentage': calc_percent,
            'cweek': now.strftime('%w'),
            'cmonth': now.month,
            'cmonthf': now.strftime('%B'),
            'strptime': datetime.strptime,
            'month_abbr': month_abbr,
        }

    return app
