# application/decorators.py

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from flask import abort, g

def confirm_email(func):
    '''Check if email has been confirmed'''

    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated and not current_user.verified :
            flash(f' You\'re Yet To Verify Your Account!', 'danger')
            return redirect(url_for('auth.unverified'))
        return func(*args, **kwargs)
    return wrapper_function



def role_required(role_type):
    def decorator(view_function):
        @wraps(view_function)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.signin'))
                abort(401)  # Unauthorized
            user_has_role = any( r.type == role_type for r in current_user.role)
            if not user_has_role:
                abort(403)  # Forbidden
            return view_function(*args, **kwargs)
        return wrapper
    return decorator



