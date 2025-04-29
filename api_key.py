"""
API Key middleware for the 0xC Chat API.
"""

from functools import wraps
from flask import request, jsonify
from env import SECRET_KEY, SECRET_KEY_ENABLED

def api_key_required(f):
    """
    Decorator to check if the API key is valid.
    
    This decorator is only active if SECRET_KEY_ENABLED is True.
    When enabled, all requests must include X-API-Key header with the correct SECRET_KEY.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # If SECRET_KEY_ENABLED is False, skip the check
        if not SECRET_KEY_ENABLED:
            return f(*args, **kwargs)
        
        # Check if X-API-Key header is present
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key is missing'
            }), 401
        
        # Check if the API key is valid
        if api_key != SECRET_KEY:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401
        
        # API key is valid, proceed
        return f(*args, **kwargs)
    
    return decorated
