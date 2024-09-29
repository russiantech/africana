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


def role_required(*required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.signin'))
                #abort(401)  # Unauthorized

            user_has_role = any( role in [role.type for role in current_user.role] for role in required_roles)
            
            return view_func(*args, **kwargs) if user_has_role else abort(403)
            
            if not user_has_role:
                abort(403) 
            else:
                #print(f"{user_has_role}") #True/False
                return view_func(*args, **kwargs)
            """ user_roles = [role.type for role in current_user.role]
            if any(role in user_roles for role in required_roles):
                return view_func(*args, **kwargs)
            else:
                abort(403)  # Forbidden """
        return wrapper
    return decorator

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



def role_required(*required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.signin'))
                #abort(401)  # Unauthorized

            user_has_role = any( required_roles in [role.type for role in current_user.role] for required_roles in required_roles)
            if not user_has_role:
                abort(403) 
            else:
                 return view_func(*args, **kwargs)
            """ user_roles = [role.type for role in current_user.role]
            if any(role in user_roles for role in required_roles):
                return view_func(*args, **kwargs)
            else:
                abort(403)  # Forbidden """
        return wrapper
    return decorator

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


def role_required1(*required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.signin'))
                abort(401)  # Unauthorized

            user_roles = [role.type for role in current_user.role]
            if any(role in user_roles for role in required_roles):
                return view_func(*args, **kwargs)
            else:
                abort(403)  # Forbidden
        return wrapper
    return decorator

