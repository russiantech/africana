from functools import wraps
from flask import request, jsonify
from web.models import db


# Custom decorator for database session management

""" def db_session_management(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        try:
            # Check if a transaction is already active
            is_session_active = db.session.is_active

            # Use a context manager to manage the session
            with db.session.begin_nested():
                result = route_function(*args, **kwargs)

            # Commit the transaction only if it was started in this decorator
            if not is_session_active:
                db.session.commit()

            return result

        except Exception as e:
            # Rollback the transaction in case of an exception
            referrer = request.headers.get('Referer')
            db.session.rollback()
            response = {'flash': 'alert-warning', 'link': str(referrer), 'response': str(e)}
            return jsonify(response), 500

    return decorated_function """

#main ************
def db_session_management(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        try:
            # Check if a transaction is already active, if not, begin a new one
            #this prevent transaction already started error
            if not db.session.is_active:
                db.session.begin()
                #db.session.begin_nested()
            
            result = route_function(*args, **kwargs)
            
            # Commit the transaction only if it was started in this decorator
            if not db.session.is_active:
                db.session.commit()
            
            return result
        
        except Exception as e:
            # Rollback the transaction in case of an exception
            db.session.rollback()
            referrer =  request.headers.get('Referer') 
            #raise
            response = {'flash': 'alert-warning', 'link': str(referrer), 'response': str(e)}
            return jsonify(response), 500
        
        finally:
            if not db.session.is_active:
                db.session.close()

    return decorated_function


""" def db_session_management(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        try:
            # Check if a transaction is already active, if not, begin a new one
            # This prevents a transaction already started error
            if not db.session.is_active:
                db.session.begin_nested()
            
            result = route_function(*args, **kwargs)
            
            # Commit the transaction only if it was started in this decorator
            if not db.session.is_active:
                db.session.commit()
            
            return result
        
        except SQLAlchemyError as e:
            # Rollback the transaction in case of a database-related exception
            db.session.rollback()
            referrer = request.headers.get('Referer') 
            response = {'flash': 'alert-warning', 'link': str(referrer), 'response': str(e)}
            return jsonify(response), 500 
        except Exception as e:
            db.session.rollback()
            referrer = request.headers.get('Referer') 
            response = {'flash': 'alert-warning', 'link': str(referrer), 'response': str(e)}
            return jsonify(response), 500

        finally:
            if not db.session.is_active:
                db.session.close()

    return decorated_function """


""" def db_session_management(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        max_retries = 3  # Maximum number of retry attempts
        retry_interval = 5  # Number of seconds to wait between retries
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Check if a transaction is already active, if not, begin a new one
                # This prevents the "transaction already started" error
                if not db.session.is_active:
                    db.session.begin()

                result = route_function(*args, **kwargs)

                # Commit the transaction only if it was started in this decorator
                if not db.session.is_active:
                    db.session.commit()

                return result

            except SQLAlchemyError as e:
                # Handle the exception (e.g., log it)
                print(f"Database error: {str(e)}")

                if isinstance(e.orig, OperationalError):
                    # Handle MySQL OperationalError (lost connection)
                    print("Attempting to reconnect...")
                    time.sleep(retry_interval)
                elif retry_count < max_retries - 1:
                    # If there are more retries left for other errors, wait and retry
                    time.sleep(retry_interval)
                else:
                    # If no more retries are left, raise an exception or return an error response
                    referrer = request.headers.get('Referer')
                    db.session.rollback()
                    response = {'flash': 'alert-warning', 'link': str(referrer), 'response': str(e)}
                    return jsonify(response), 500

                retry_count += 1

            finally:
                if not db.session.is_active:
                    db.session.close()

    return decorated_function """


""" The decorator checks if an active transaction is already in progress using db.session.is_active. 
If no transaction is active, it starts a new one with db.session.begin(). 
It then commits the transaction only if it was started within the decorator.
This approach ensures that the decorator works seamlessly with routes that may or may not start a transaction. 
If a route has already started a transaction, the decorator won't interfere with it. 
If a route hasn't started a transaction, the decorator will start and commit one as needed. 
This way, you can use the decorator without issues regardless of the transaction state. 
//
In the provided db_session_management decorator, a finally block is not required because the decorator uses a context manager to manage the session. Context managers, 
such as the with statement, are designed to automatically handle cleanup actions like committing or rolling back resources when they go out of scope, including when exceptions occur.
//
Here's how the decorator works:

It checks if a transaction is already active using db.session.is_active.
It then enters a nested transaction using with db.session.begin_nested():. This nested transaction allows you to perform operations within the context of the current session, 
and it will be committed or rolled back automatically when the block exits.
Inside the nested transaction, it calls the route_function to perform the desired database operations.
After the with block exits, it checks whether the transaction was started by the decorator (if not is_session_active) and commits the transaction if necessary.
If an exception occurs within the with block, it automatically rolls back the transaction, and the exception is caught and handled.
The with statement ensures that the session is managed correctly, and any changes made within the block are either committed or rolled back as needed. 
Therefore, there's no need for an explicit finally block in this decorator, as the context manager takes care of it.
 """






