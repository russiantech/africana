# Utility functions for responses
from flask import jsonify

def success_response(message, data=None):
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data.to_dict() if hasattr(data, 'to_dict') else data
    return jsonify(response), 200

def error_response(message):
    return jsonify({'success': False, 'error': message}), 400

class SequentialGenerator:
    def __init__(self, start=1):
        self.counter = start

    def next(self):
        current_value = self.counter
        self.counter += 1
        return current_value

# Create an instance of the SequentialGenerator
generator = SequentialGenerator(start=10)
# version=generator.next()