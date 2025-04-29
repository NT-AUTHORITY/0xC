"""
Authentication utilities for the 0xC Chat API.
"""

from functools import wraps
from flask import request, jsonify
from models import User

def token_required(f):
    """
    Decorator to protect routes that require authentication.
    
    This decorator extracts the JWT token from the Authorization header,
    validates it, and passes the authenticated user to the decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header is present
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Extract token from "Bearer <token>"
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Authentication token is missing'
            }), 401
        
        # Decode and validate token
        payload = User.decode_token(token)
        if 'error' in payload:
            return jsonify({
                'status': 'error',
                'message': payload['error']
            }), 401
        
        # Check token type
        if payload.get('token_type') != 'access':
            return jsonify({
                'status': 'error',
                'message': 'Invalid token type'
            }), 401
        
        # Get user from token
        user = User.get_by_id(payload['user_id'])
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 401
        
        # Pass user to the decorated function
        return f(user, *args, **kwargs)
    
    return decorated
