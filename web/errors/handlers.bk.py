from flask import Blueprint, render_template, abort, current_app
from flask_login import current_user
errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(403)
def error_403(error):

    return current_user.role[0].type
    if current_user.is_authenticated:
        roles = [role.type for role in current_user.role]
        roles = [role.type for role in current_user.role]
            if 'admin' in roles:
                return redirect(url_for('main.index'))
            elif 'kitchen' in roles:
                return redirect(url_for('main.kitchen'))
            elif 'cocktail' in roles:
                return redirect(url_for('main.cocktail'))
            elif 'bar' in roles:
                return redirect(url_for('main.bar'))
            else:
                return redirect(url_for('auth.update', usrname=current_user.username))
        else:
            return current_app.login_manager.unauthorized()
    return render_template('errors/403.html'), 403

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500

@errors.app_errorhandler(413)
def error_413(error):
    
    return render_template('errors/403.html'), 413