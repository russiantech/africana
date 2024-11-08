# from flask import jsonify, Blueprint, request
# from flask_login import current_user, login_required
# from sqlalchemy import update
# from web import db
# from web.models import (
#     Items, Apportion, StockHistory
# )
# from web.utils.sequence_int import generator
# from web.utils.db_session_management import db_session_management

# apportion_items_bp = Blueprint('apportion_items', __name__)

# # Utility function to handle success responses
# def success_response(message):
#     return jsonify({'success': True, 'message': message})

# # Utility function to handle error responses
# def error_response(message):
#     return jsonify({'success': False, 'error': message})

# @apportion_items_bp.route('/get-items-series', methods=['GET'])
# def item_series():
#     try:
#         selected_department = request.args.get('dept')
#         if not selected_department:
#             return error_response("No department provided.")
        
#         # Query the product series for the selected department
#         product_series = Item.query.filter_by(dept=selected_department).with_entities(Item.id, Item.name).all()
#         product_series_data = [{'id': item[0], 'name': item[1]} for item in product_series]
#         return jsonify(product_series_data)
    
#     except Exception as e:
        
#         return error_response(f"Error fetching product series: {str(e)}")

# # Create apportioned item
# @apportion_items_bp.route('/insert-apportion-items', methods=['POST'])
# @login_required
# @db_session_management
# def insert_item():
#     try:
#         data = request.get_json()
#         items_title = data.get('items_title')
#         items_dept = data.get('items_dept')
#         items_qty = data.get('items_qty')

#         if not items_title or not items_dept or not items_qty:
#             # return error_response("Missing required fields: items_title, items_dept, or items_qty")
#             return error_response("Missing required fields: Title, Department, or Quantity")

#         apportioned_item = Apportion(
#             user_id=current_user.id if current_user.is_authenticated else 0,
#             items_title=items_title,
#             items_dept=items_dept,
#             items_qty=items_qty,
#             deleted=False
#         )
#         db.session.add(apportioned_item)
#         db.session.commit()

#         # Record stock history
#         stock_history = StockHistory(
#             apportioned_item_id=apportioned_item.id,
#             user_id=current_user.id,
#             version=generator.next(),
#             difference=items_qty,
#             in_stock=items_qty,
#             desc=f"{items_qty} portions of {items_title} apportioned by {current_user.username}"
#         )
#         db.session.add(stock_history)
#         db.session.commit()

#         return success_response(f"Successfully apportioned {items_title}")
    
#     except Exception as e:
#         db.session.rollback()  # Rollback in case of error
#         return error_response(f"Error apportioning item: {str(e)}")

# # Fetch all apportioned items or a specific apportioned item by ID
# @apportion_items_bp.route('/apportion-items', methods=['GET'])
# @apportion_items_bp.route('/apportion-items/<int:item_id>', methods=['GET'])
# @login_required
# @db_session_management
# def fetch_apportioned_items(item_id=None):
#     try:
#         if item_id:
#             # Fetch specific apportioned item by ID
#             apportioned_item = Apportion.query.get(item_id)
#             if not apportioned_item:
#                 return error_response("Apportioned item not found.")
#             return success_response(apportioned_item.to_dict())  # Assuming a to_dict method for serialization
#         else:
#             # Fetch all apportioned items
#             page = request.args.get('page', 1, type=int)
#             per_page = request.args.get('per_page', 10, type=int)

#             apportioned_items_pagination = Apportion.query.paginate(page=page, per_page=per_page, error_out=False)
#             apportioned_items = [item.to_dict() for item in apportioned_items_pagination.items]

#             return success_response({
#                 "items": apportioned_items,
#                 "total_items": apportioned_items_pagination.total,
#                 "total_pages": apportioned_items_pagination.pages,
#                 "current_page": apportioned_items_pagination.page
#             })
    
#     except Exception as e:
#         return error_response(f"Error fetching apportioned items: {str(e)}")

# # Update apportioned item
# @apportion_items_bp.route('/update/<int:item_id>/apportion-items', methods=['PUT'])
# @login_required 
# @db_session_management
# def update_item(item_id):
#     try:
#         apportioned_item = Apportion.query.get(item_id)
#         if not apportioned_item:
#             return error_response("Apportioned item not found.")

#         data = request.get_json()
#         items_title = data.get('items_title')
#         items_qty = data.get('items_qty')

#         if items_title:
#             apportioned_item.items_title = items_title
#         if items_qty:
#             apportioned_item.items_qty = items_qty

#         # Record the update in stock history
#         stock_difference = apportioned_item.items_qty - int(items_qty)
#         stock_history = StockHistory(
#             apportioned_item_id=item_id,
#             user_id=current_user.id,
#             version=generator.next(),
#             difference=stock_difference,
#             in_stock=apportioned_item.items_qty,
#             desc=f"{current_user.username} updated {apportioned_item.items_title}"
#         )
        
#         db.session.add(stock_history)
#         db.session.commit()

#         return success_response(f"Successfully updated apportioned item: {items_title}")
    
#     except Exception as e:
        
#         db.session.rollback()  # Rollback on error
#         return error_response(f"Error updating apportioned item: {str(e)}")

# # Delete apportioned item
# @apportion_items_bp.route('/delete/<int:item_id>/apportion-items', methods=['DELETE'])
# @login_required
# @db_session_management
# def delete_item(item_id):
#     try:
#         apportioned_item = Apportion.query.get(item_id)
#         if not apportioned_item:
#             return error_response("Apportioned item not found.")

#         db.session.delete(apportioned_item)

#         # Optionally delete stock history
#         history_entry = StockHistory.query.filter_by(apportioned_item_id=item_id).first()
#         if history_entry:
#             db.session.delete(history_entry)

#         db.session.commit()
#         return success_response(f"Successfully deleted apportioned item: {apportioned_item.items_title}")
    
#     except Exception as e:
    
#         db.session.rollback()  # Rollback on error
#         return error_response(f"Error deleting apportioned item: {str(e)}")


# import traceback
# from flask import Blueprint, request, jsonify
# from flask_login import current_user
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# from web.models import (
#     db, Apportion
# )

# apportion_items_bp = Blueprint('apportion_items', __name__)

# # Utility functions for responses

# def success_response(message, data=None):
#     response = {'success': True, 'message': message}
#     if data is not None:
#         response['data'] = data.to_dict() if hasattr(data, 'to_dict') else data
#     return jsonify(response)

# def error_response(message):
#     return jsonify({'success': False, 'error': message})

# # Create a new apportioned item
# @apportion_items_bp.route('/apportioneditems', methods=['POST'])
# def create_apportioned_item():
#     try:
#         data = request.json
#         # print(data)  # For debugging
        
#         # Set default values for qty and cost
#         items_qty = data.get('items_qty')
#         items_cost = data.get('items_cost')
        
#         # Convert to integer, defaulting to 0 if None or invalid
#         items_qty = int(items_qty) if items_qty and items_qty.isdigit() else 0
#         items_cost = int(items_cost) if items_cost and items_cost.isdigit() else 0
        
#         new_item = Apportion(
#             user_id=data.get('user_id', current_user.id),
#             items_dept=data.get('items_dept', 'k'),
#             items_title=data.get('items_title'),
#             items_qty=items_qty,
#             items_cost=items_cost,
#             # parent_id=data.get('parent_id') 
#         )
        
#         db.session.add(new_item)
#         db.session.commit()
#         return success_response("Apportioned item created successfully.", data=data)
#         # return success_response("Apportioned item created successfully.")
    
#     except IntegrityError:
#         db.session.rollback()
#         traceback.print_exc()
#         return error_response("Failed to create apportioned item: Integrity error.")
    
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return error_response(f"Database error: {str(e)}")
    
#     except Exception as e:
#         return error_response(f"Unexpected error: {str(e)}")


# # # Fetch all apportioned items or a specific apportioned item by ID
# @apportion_items_bp.route('/apportion-items', methods=['GET'])
# @apportion_items_bp.route('/apportion-items/<int:item_id>', methods=['GET'])
# # @login_required
# def fetch_apportioned_items(item_id=None):
#     try:
#         if item_id:
#             # Fetch specific apportioned item by ID
#             apportioned_item = Apportion.query.get(item_id)
#             if not apportioned_item:
#                 return error_response("Apportioned item not found.")
#             return success_response(apportioned_item.to_dict())  # Assuming a to_dict method for serialization
#         else:
#             # Fetch all apportioned items
#             page = request.args.get('page', 1, type=int)
#             per_page = request.args.get('per_page', 10, type=int)

#             apportioned_items_pagination = Apportion.query.paginate(page=page, per_page=per_page, error_out=False)
#             apportioned_items = [item.to_dict() for item in apportioned_items_pagination.items]

#             return success_response({
#                 "items": apportioned_items,
#                 "total_items": apportioned_items_pagination.total,
#                 "total_pages": apportioned_items_pagination.pages,
#                 "current_page": apportioned_items_pagination.page
#             })
    
#     except Exception as e:
#         return error_response(f"Error fetching apportioned items: {str(e)}")

# @apportion_items_bp.route('/apportioneditems-by-hierachy', methods=['GET'])
# def get_apportioned_items():
#     """ 
#         Example Requests/Usage
#         Fetch Main Products (Parent products):
#         GET /apportioneditems
#         Fetch Apportioned Products (From a Main Product):

#         GET /apportioneditems?main_product_id=1
#         Fetch Extracted Products (From an Apportioned Product):

#         GET /apportioneditems?apportioned_id=5
#         This approach consolidates the logic, reduces redundant code, and keeps the flexibility to fetch different types of products in one route.
#     """
#     try:
#         # Fetching parameters from request arguments
#         main_product_id = request.args.get('main_product_id')
#         apportioned_id = request.args.get('apportioned_id')
        
#         # Determine which set of products to fetch based on the presence of the parameters
#         if main_product_id is None and apportioned_id is None:
#             # Fetch main products (parent_id is None)
#             products = Apportion.query.filter(Apportion.parent_id.is_(None)).all()
#             response_message = "Main products fetched successfully."
#         elif main_product_id is not None:
#             # Fetch apportioned products (parent_id equals main_product_id)
#             products = Apportion.query.filter_by(parent_id=main_product_id).all()
#             response_message = "Apportioned products fetched successfully."
#         elif apportioned_id is not None:
#             # Fetch extracted products (parent_id equals apportioned_id)
#             products = Apportion.query.filter_by(parent_id=apportioned_id).all()
#             response_message = "Extracted products fetched successfully."
#         else:
#             return error_response("Invalid request parameters.")
        
#         # Return the data in a successful response
#         return success_response(response_message, data=[item.to_dict() for item in products])

#     except SQLAlchemyError as e:
#         return error_response(f"Database error: {str(e)}")

# # Read an apportioned item by ID
# # @apportion_items_bp.route('/apportioneditems/<int:item_id>', methods=['GET'])
# # def get_apportioned_item(item_id):
# #     item = Apportion.query.get(item_id)
# #     if item:
# #         return jsonify({
# #             'id': item.id,
# #             'user_id': item.user_id,
# #             'items_dept': item.items_dept,
# #             'items_title': item.items_title,
# #             'items_qty': item.items_qty,
# #             'items_cost': item.items_cost,
# #             'created': item.created.isoformat()
# #         })
# #     return error_response("Apportioned item not found.")

# # Update an apportioned item
# @apportion_items_bp.route('/apportioneditems/<int:item_id>', methods=['PUT'])
# def update_apportioned_item(item_id):
#     try:
#         item = Apportion.query.get(item_id)
#         if item is None:
#             return error_response("Apportioned item not found.")
        
#         data = request.json
#         item.user_id = data.get('user_id', item.user_id)
#         item.items_dept = data.get('items_dept', item.items_dept)
#         item.items_title = data.get('items_title', item.items_title)
#         item.items_qty = data.get('items_qty', item.items_qty)
#         item.items_cost = data.get('items_cost', item.items_cost)
#         item.parent_id = data.get('parent_id', item.parent_id)
        
#         db.session.commit()
#         return success_response("Apportioned item updated successfully.")
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return error_response(f"Database error: {str(e)}")
#     except Exception as e:
#         return error_response(f"Unexpected error: {str(e)}")

# # Delete an apportioned item
# @apportion_items_bp.route('/apportioneditems/<int:item_id>', methods=['DELETE'])
# def delete_apportioned_item(item_id):
#     try:
#         item = Apportion.query.get(item_id)
#         if item is None:
#             return error_response("Apportioned item not found.")

#         db.session.delete(item)
#         db.session.commit()
#         return success_response("Apportioned item deleted successfully.")
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return error_response(f"Database error: {str(e)}")
#     except Exception as e:
#         return error_response(f"Unexpected error: {str(e)}")
    

# def take_out_bags(apportioned_item_id, quantity_to_take):
#     """Take out a specified quantity from the apportioned item."""
#     item = Apportion.query.get(apportioned_item_id)
    
#     if item is None:
#         print(f"Item with ID {apportioned_item_id} not found.")
#         return
    
#     if item.items_qty < quantity_to_take:
#         print(f"Not enough stock to take out {quantity_to_take} bags from {item.items_title}. Current stock: {item.items_qty}.")
#         return

#     item.items_qty -= quantity_to_take  # Update quantity
#     db.session.commit()  # Commit the changes
#     print(f"Removed {quantity_to_take} bags from {item.items_title}. New quantity: {item.items_qty}.")
#     log_stock_movement(item.id, -quantity_to_take)


# def return_bags(apportioned_item_id, quantity_to_return):
#     """Return a specified quantity to the apportioned item."""
#     item = Apportion.query.get(apportioned_item_id)
    
#     if item is None:
#         print(f"Item with ID {apportioned_item_id} not found.")
#         return

#     item.items_qty += quantity_to_return  # Update quantity
#     db.session.commit()  # Commit the changes
#     print(f"Returned {quantity_to_return} bags to {item.items_title}. New quantity: {item.items_qty}.")
#     log_stock_movement(item.id, quantity_to_return)

# def log_stock_movement(apportioned_item_id, quantity_change):
#     """Log the stock movement details to the console."""
#     action = "added to" if quantity_change > 0 else "removed from"
#     print(f"{abs(quantity_change)} bags {action} item ID {apportioned_item_id}.")

# @apportion_items_bp.route('/apportioneditems/<int:item_id>/takeout', methods=['POST'])
# def api_take_out_bags(item_id):
#     """Take out bags from an apportioned item."""
#     try:
#         data = request.json
#         quantity_to_take = data.get('quantity')
        
#         if quantity_to_take is None or quantity_to_take <= 0:
#             return error_response("Invalid quantity specified.")
        
#         item = Apportion.query.get(item_id)
#         if item is None:
#             return error_response("Apportioned item not found.")
        
#         if item.items_qty < quantity_to_take:
#             return error_response(f"Not enough stock to take out {quantity_to_take} bags from {item.items_title}. Current stock: {item.items_qty}.")
        
#         # Call the utility function to take out bags
#         take_out_bags(item_id, quantity_to_take)
#         return success_response(f"Successfully took out {quantity_to_take} bags from {item.items_title}.")
    
#     except Exception as e:
#         return error_response(f"Error: {str(e)}")


# @apportion_items_bp.route('/apportioneditems/<int:item_id>/return', methods=['POST'])
# def api_return_bags(item_id):
#     """Return bags to an apportioned item."""
#     try:
#         data = request.json
#         quantity_to_return = data.get('quantity')
        
#         if quantity_to_return is None or quantity_to_return <= 0:
#             return error_response("Invalid quantity specified.")
        
#         item = Apportion.query.get(item_id)
#         if item is None:
#             return error_response("Apportioned item not found.")
        
#         # Call the utility function to return bags
#         return_bags(item_id, quantity_to_return)
#         return success_response(f"Successfully returned {quantity_to_return} bags to {item.items_title}.")
    
#     except Exception as e:
#         return error_response(f"Error: {str(e)}")


""" 
==================================================================================================================
    FOR THE NEW DESIGN & APPORTION MODEL
==================================================================================================================
"""

import traceback
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from web.models import Extraction, db, Apportion
from web.apis.utils import success_response, error_response

# apportion_bp = Blueprint('apportion', __name__)
apportion_items_bp = Blueprint('apportion_items', __name__)

# Create a new apportion record
@apportion_items_bp.route('/apportions', methods=['POST'])
def insert_apportion():
    try:
        data = request.json
        new_apportion = Apportion(
            product_title=data.get('product_title'),
            dept=data.get('apportion_dept', 'k'),
            main_qty=data.get('main_qty', 0),
            initial_apportioning=data.get('initial_apportioning', 0),
            apportioned_qty=data.get('apportioned_qty', data.get('initial_apportioning') ),
            extracted_qty=data.get('extracted_qty', 0),
            cost_price=data.get('cost_price', 0),
        )
        
        db.session.add(new_apportion)
        db.session.commit()
        return success_response("Apportion created successfully.", data=new_apportion)
    
    except IntegrityError:
        db.session.rollback()
        traceback.print_exc()
        return error_response("Failed to create apportion: Integrity error.")
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}")
    
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}")
    
# Fetch all apportion records or a specific record by ID, with latest records coming first
@apportion_items_bp.route('/apportions', methods=['GET'])
@apportion_items_bp.route('/apportions/<int:apportion_id>', methods=['GET'])
def fetch_apportions(apportion_id=None):
    try:
        # Fetch specific apportion record by ID
        if apportion_id:
            apportion = Apportion.query.get(apportion_id)
            if not apportion:
                return error_response("Apportion not found.")
            return success_response("Apportion fetched successfully.", data=apportion.to_dict())

        # Pagination settings
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Fetch paginated apportions, ordered by latest
        apportion_pagination = Apportion.query.order_by(Apportion.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        apportions = [item.to_dict() for item in apportion_pagination.items]

        # Prepare paginated response data
        data = {
            "current_page": apportion_pagination.page,
            "items": apportions,
            "total_items": apportion_pagination.total,
            "total_pages": apportion_pagination.pages
        }
        return success_response("Apportion items fetched successfully.", data=data)

    except Exception as e:
        traceback.print_exc()
        return error_response(f"Error fetching apportion records: {str(e)}")


# Update an apportion record
@apportion_items_bp.route('/apportions/<int:apportion_id>', methods=['PUT'])
def update_apportion(apportion_id):
    try:
        apportion = Apportion.query.get(apportion_id)
        if apportion is None:
            return error_response("Apportion not found.")
        
        data = request.json
        apportion.product_title = data.get('product_title', apportion.product_title)
        apportion.dept = data.get('dept', apportion.dept)
        apportion.main_qty = data.get('main_qty', apportion.main_qty)
        apportion.initial_apportioning = data.get('initial_apportioning', apportion.initial_apportioning)
        apportion.apportioned_qty = data.get('apportioned_qty', apportion.apportioned_qty)
        apportion.extracted_qty = data.get('extracted_qty', apportion.extracted_qty)
        apportion.cost_price = data.get('cost_price', apportion.cost_price)
        
        db.session.commit()
        return success_response("Apportion updated successfully.")
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}")
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}")

# Delete an apportion record
@apportion_items_bp.route('/apportions/<int:apportion_id>', methods=['DELETE'])
def delete_apportion(apportion_id):
    try:
        apportion = Apportion.query.get(apportion_id)
        if apportion is None:
            return error_response("Apportion Product Not Found.")

        db.session.delete(apportion)
        db.session.commit()
        return success_response("Apportion Item deleted successfully.")
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}")
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}")

# Adjust quantities
def adjust_quantity(apportion_id, quantity_change, action):
    apportion = Apportion.query.get(apportion_id)
    if apportion:
        if action == "takeout":
            if apportion.apportioned_qty < quantity_change:
                print("Not enough stock to take out.")
                return
            apportion.apportioned_qty -= quantity_change
        elif action == "return":
            apportion.apportioned_qty += quantity_change
        db.session.commit()
        print(f"{quantity_change} quantity {action}d.")
    else:
        print("Apportion record not found.")

@apportion_items_bp.route('/apportion/<int:apportion_id>/takeout', methods=['POST'])
def api_take_out_bags(apportion_id):
    try:
        data = request.json
        quantity_to_take = data.get('quantity')
        
        if quantity_to_take is None or quantity_to_take <= 0:
            return error_response("Invalid quantity specified.")
        
        apportion = Apportion.query.get(apportion_id)
        if apportion is None:
            return error_response("Apportion record not found.")
        
        if apportion.apportioned_qty < quantity_to_take:
            return error_response(f"Not enough stock to take out {quantity_to_take} from {apportion.product_title}.")
        
        adjust_quantity(apportion_id, quantity_to_take, action="takeout")
        return success_response(f"Successfully took out {quantity_to_take} from {apportion.product_title}.")
    
    except Exception as e:
        return error_response(f"Error: {str(e)}")

@apportion_items_bp.route('/apportion/<int:apportion_id>/return', methods=['POST'])
def api_return_bags(apportion_id):
    try:
        data = request.json
        quantity_to_return = data.get('quantity')
        
        if quantity_to_return is None or quantity_to_return <= 0:
            return error_response("Invalid quantity specified.")
        
        apportion = Apportion.query.get(apportion_id)
        if apportion is None:
            return error_response("Apportion record not found.")
        
        adjust_quantity(apportion_id, quantity_to_return, action="return")
        return success_response(f"Successfully returned {quantity_to_return} to {apportion.product_title}.")
    
    except Exception as e:
        return error_response(f"Error: {str(e)}")


""" 
==================================================================================================================
    FOR THE EXTRACTION MODEL
==================================================================================================================
"""

# Create a new extraction record
@apportion_items_bp.route('/extractions', methods=['POST'])
def insert_extraction():
    try:
        data = request.json
        apportion_id = int(data.get('apportion_id', 0))
        extracted_qty = int(data.get('extracted_qty', None))

        # Fetch the Apportion item based on provided ID
        if apportion_id:
            apportion = Apportion.query.filter(
                (Apportion.id == apportion_id) & (Apportion.deleted.is_(False))
            ).first()
        
        if apportion is None:
            return error_response(f"Apportion not found for the provided ID.{apportion_id}")

        # Ensure extracted_qty is provided and valid
        if extracted_qty is None or extracted_qty <= 0:
            return error_response("Invalid extracted quantity provided.")

        # Check if there is enough quantity in the apportion to extract
        if apportion.apportioned_qty < int(extracted_qty):
            return error_response(f"Not enough quantity available in apportion. You have {apportion.apportioned_qty } left to extract.")

        # Create a new extraction record
        extraction = Extraction(
            extracted_title=data['extracted_title'],
            apportion_id=apportion_id,
            extracted_qty=extracted_qty,
            remaining_stock=apportion.apportioned_qty - extracted_qty,
            descr=data.get('descr', None)
        )

        # Deduct the extracted quantity from the main apportion quantity
        apportion.apportioned_qty -= extracted_qty

        # Save the extraction and update the apportion quantity in the database
        db.session.add(extraction)
        db.session.commit()

        return success_response("Extraction created successfully.", data=extraction.to_dict())
    
    except SQLAlchemyError as e:
        db.session.rollback()
        traceback.print_exc()
        return error_response(f"Database error: {str(e)}")
    
    except Exception as e:
        traceback.print_exc()
        return error_response(f"Unexpected error: {str(e)}")

@apportion_items_bp.route('/extractions/<int:extraction_id>', methods=['PUT'])
def update_extraction(extraction_id):
    try:
        
        """ 
            This part of the update function is specifically for cases where we are modifying the `extracted_qty` for an existing 
            `Extraction` record without changing its associated `apportion_id`. Here’s what’s happening and why each step is necessary:

            Explanation of Each Step

            1.Identify Quantity Difference:**
            
            qty_difference = new_extracted_qty - extraction.extracted_qty
            
            We calculate `qty_difference`, which is the difference between the new extraction quantity (`new_extracted_qty`) provided in the update request and the current `extracted_qty` stored in the database. 
            This tells us if:
            - We’re increasing the extraction quantity (i.e., `qty_difference > 0`)
            - We’re decreasing it (i.e., `qty_difference < 0`)
            - Or if it remains the same (i.e., `qty_difference = 0`)

            2.Check Available Apportion Quantity if Extracted Quantity Increases:**
            
            if qty_difference > 0 and apportion.apportioned_qty < qty_difference:
                return error_response(f"Not enough quantity in apportion. Available: {apportion.apportioned_qty}.")
            
            If `qty_difference` is positive, it means we’re attempting to increase the amount extracted. Therefore, we need to check if the associated `Apportion` has enough remaining quantity (`apportioned_qty`) to support this increase:
            - If `apportion.apportioned_qty < qty_difference`, the update fails, and an error is returned to inform the user there isn’t enough stock available to meet this requested increase.

            3.Adjust Apportioned Quantity Based on Difference:**
            
            apportion.apportioned_qty -= qty_difference
            
            After ensuring there’s sufficient quantity available, we update the `apportioned_qty` in the `Apportion` model by deducting `qty_difference`. 
            This updates the `apportioned_qty` in `Apportion` to accurately reflect the remaining stock after the extraction change.

            Why This Approach?

            When modifying `extracted_qty`, the apportion’s `apportioned_qty` needs to reflect this change to maintain data consistency and prevent over-extraction. For instance:
            -If we increase `extracted_qty`,** we reduce `apportioned_qty` accordingly to show the reduction in stock.
            -If we decrease `extracted_qty`,** `qty_difference` becomes negative, so adding it back to `apportioned_qty` accurately reflects the returned stock.

            This logic preserves data integrity by ensuring `apportioned_qty` accurately tracks remaining stock after each extraction modification.

        """
        # extraction = Extraction.query.get(extraction_id)
        if extraction_id:
            extraction = Extraction.query.filter(
                (Extraction.id == extraction_id) & (Extraction.deleted.is_(False))
            ).first()
            
        if extraction is None:
            return error_response("Extraction not found.")
        
        data = request.json
        new_apportion_id = data.get('apportion_id', extraction.apportion_id)
        new_extracted_qty = int(data.get('extracted_qty', extraction.extracted_qty))

        # Check if the apportion_id is changing and fetch the new apportion item
        if new_apportion_id != extraction.apportion_id:
            new_apportion = Apportion.query.get(new_apportion_id)
            if new_apportion is None:
                return error_response("Apportion not found for the provided ID.")
            
            # Add back the previous extracted_qty to the old apportion
            old_apportion = Apportion.query.get(extraction.apportion_id)
            old_apportion.apportioned_qty += extraction.extracted_qty

            # Deduct the new extracted_qty from the new apportion
            if new_apportion.apportioned_qty < new_extracted_qty:
                return error_response(f"Not enough quantity in the new apportion. Available: {new_apportion.apportioned_qty}.")
            new_apportion.apportioned_qty -= new_extracted_qty
            extraction.apportion_id = new_apportion_id

        else:
            # Adjust the quantity in the same apportion if extracted_qty is changed
            apportion = Apportion.query.get(extraction.apportion_id)
            qty_difference = int(new_extracted_qty - extraction.extracted_qty)
            if qty_difference > 0 and apportion.apportioned_qty < qty_difference:
                return error_response(f"Not enough quantity in apportion. Available: {apportion.apportioned_qty}.")
            
            apportion.apportioned_qty -= qty_difference

        # Update the extraction record fields
        extraction.extracted_title = data.get('extracted_title', extraction.extracted_title)
        extraction.extracted_qty = new_extracted_qty
        extraction.remaining_stock = data.get('remaining_stock', extraction.remaining_stock)
        extraction.descr = data.get('descr', extraction.descr)
        
        db.session.commit()
        return success_response("Extraction updated successfully.", data=extraction.to_dict())
    
    except SQLAlchemyError as e:
        db.session.rollback()
        traceback.print_exc()
        return error_response(f"Database error: {str(e)}")
    except Exception as e:
        traceback.print_exc()
        return error_response(f"Unexpected error: {str(e)}")


# Fetch all extractions or a specific extraction by ID
@apportion_items_bp.route('/extractions', methods=['GET'])
@apportion_items_bp.route('/extractions/<int:extraction_id>', methods=['GET'])
def fetch_extractions(extraction_id=None):
    try:
        # Fetch specific extraction record by ID
        # if extraction_id:
        #     extraction = Extraction.query.get(extraction_id)
        #     if not extraction:
        #         return error_response("Extraction not found.")
        #     return success_response("Extraction fetched successfully.", data=extraction.to_dict())
        
        if extraction_id:
            extraction = Extraction.query.filter(
                (Extraction.id == extraction_id) & (Extraction.deleted.is_(False))
            ).first()
            
            if not extraction:
                return error_response("Extraction not found.")
            return success_response("Extraction fetched successfully.", data=extraction.to_dict())
        
            
        # Pagination settings
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get department from query parameters
        dept = request.args.get('dept', None, type=str)
        query = Extraction.query
        
        # Filter by department if provided
        if dept and dept is not None:
            # query = query.filter(Extraction.apportion.dept == dept)  # Corrected the equality comparison
            query = query.join(Apportion).filter(Apportion.dept == dept)
            
        # Paginate the query results
        extraction_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        extractions = [item.to_dict() for item in extraction_pagination.items]

        # Prepare paginated response data
        data = {
            "current_page": extraction_pagination.page,
            "items": extractions,
            "total_items": extraction_pagination.total,
            "total_pages": extraction_pagination.pages
        }
        return success_response("Extractions fetched successfully.", data=data)
    
    except Exception as e:
        return error_response(f"Error fetching extraction records: {str(e)}")

# Delete an extraction record
@apportion_items_bp.route('/extractions/<int:extraction_id>', methods=['DELETE'])
def delete_extraction(extraction_id):
    try:
        extraction = Extraction.query.get(extraction_id)
        if extraction is None:
            return error_response("Extraction not found.")

        db.session.delete(extraction)
        db.session.commit()
        return success_response("Extraction deleted successfully.")
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}")
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}")
