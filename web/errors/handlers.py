from flask import Blueprint, render_template, abort, current_app, redirect, url_for
from flask_login import current_user

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def error_404(error):
    """ user_url = direct_user(current_user) """
    user_url = redirect(url_for('auth.update', usrname=current_user.username) if current_user.is_authenticated else url_for('main.index'))
    return render_template('errors/404.html', user_url=user_url), 404

@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500

@errors.app_errorhandler(413)
def error_413(error):
    return render_template('errors/403.html'), 413
