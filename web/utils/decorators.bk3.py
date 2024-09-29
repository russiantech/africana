# application/decorators.py

from functools import wraps
from flask import redirect, request, url_for, flash
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
                #return redirect(url_for('auth.signin')) 
                #return redirect(url_for('errors.403'))
                return redirect(url_for('auth.signin')) or abort(401) # Unauthorized/unauthenticated

            user_has_role = any( required_roles in [role.type for role in current_user.role] for required_roles in required_roles)
            return view_func(*args, **kwargs) if user_has_role else abort(403) #forbidden

        return wrapper
    return decorator

""" allow only admin/current_user access this routes """
def admin_or_current_user():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                #return redirect(url_for('auth.signin')) 
                #return redirect(url_for('errors.403'))
                return redirect(url_for('auth.signin')) or abort(401) # Unauthorized/unauthenticated
            
            """ requested_username = kwargs.get('usrname')
            if current_user.username != requested_username:
                abort(403)  # Forbidden """
            requested_username = kwargs.get('usrname')
            #if ( (current_user.is_admin()) | (current_user.username == usr.username) ):
            if ( (current_user.is_admin()) | (current_user.username == requested_username)  ):
                return view_func(*args, **kwargs) 
            else:
                #return f"{current_user.username}, {request.args.get('usrname')}, {requested_username}"
                abort(403) #forbidden

        return wrapper
    return decorator
