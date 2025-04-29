"""
Authentication routes for the 0xC Chat API.
"""

from flask import Blueprint, request, jsonify
from models import User
from env import ACCESS_TOKEN_EXPIRES, REFRESH_TOKEN_EXPIRES, REGISTER_ENABLED
from api_key import api_key_required

# Create a Blueprint for the authentication routes
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
@api_key_required
def register():
    """Register a new user."""
    # Check if registration is enabled
    if not REGISTER_ENABLED:
        return jsonify({
            'status': 'error',
            'message': 'User registration is disabled'
        }), 403

    data = request.get_json()

    # Validate request data
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No input data provided'
        }), 400

    # Check required fields
    required_fields = ['username', 'password']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400

    # Validate username length
    if len(data['username']) < 3:
        return jsonify({
            'status': 'error',
            'message': 'Username must be at least 3 characters long'
        }), 400

    # Validate password strength
    if len(data['password']) < 8:
        return jsonify({
            'status': 'error',
            'message': 'Password must be at least 8 characters long'
        }), 400

    # Check if username already exists
    if User.get_by_username(data['username']):
        return jsonify({
            'status': 'error',
            'message': 'Username already exists'
        }), 409

    # Create new user
    email = data.get('email')
    user = User.register(data['username'], data['password'], email)

    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'data': user.to_dict()
    }), 201

@auth.route('/login', methods=['POST'])
@api_key_required
def login():
    """Authenticate a user and return tokens."""
    data = request.get_json()

    # Validate request data
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No input data provided'
        }), 400

    # Check required fields
    if 'username' not in data or 'password' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: username, password'
        }), 400

    # Authenticate user
    user = User.authenticate(data['username'], data['password'])
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Invalid username or password'
        }), 401

    # Generate tokens
    access_token = user.generate_access_token()
    refresh_token = user.generate_refresh_token()

    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_EXPIRES * 60  # Convert minutes to seconds
        }
    }), 200

@auth.route('/refresh', methods=['POST'])
@api_key_required
def refresh_token():
    """Refresh access token using refresh token."""
    data = request.get_json()

    # Validate request data
    if not data or 'refresh_token' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Refresh token is required'
        }), 400

    # Get user by refresh token
    user = User.get_by_refresh_token(data['refresh_token'])
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'Invalid or expired refresh token'
        }), 401

    # Generate new access token
    access_token = user.generate_access_token()

    return jsonify({
        'status': 'success',
        'message': 'Token refreshed successfully',
        'data': {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_EXPIRES * 60  # Convert minutes to seconds
        }
    }), 200

@auth.route('/logout', methods=['POST'])
@api_key_required
def logout():
    """Logout a user by invalidating their refresh token."""
    data = request.get_json()

    # Validate request data
    if not data or 'refresh_token' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Refresh token is required'
        }), 400

    # Invalidate refresh token
    success = User.invalidate_refresh_token(data['refresh_token'])
    if not success:
        return jsonify({
            'status': 'error',
            'message': 'Invalid refresh token'
        }), 400

    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    }), 200

@auth.route('/token-info', methods=['GET'])
@api_key_required
def token_info():
    """Get information about the current token."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({
            'status': 'error',
            'message': 'Authorization header is missing'
        }), 401

    # Extract token from "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({
            'status': 'error',
            'message': 'Invalid authorization header format'
        }), 401

    token = parts[1]

    # Decode token
    payload = User.decode_token(token)
    if 'error' in payload:
        return jsonify({
            'status': 'error',
            'message': payload['error']
        }), 401

    # Get user from token
    user = User.get_by_id(payload['user_id'])
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'User not found'
        }), 401

    return jsonify({
        'status': 'success',
        'data': {
            'user': user.to_dict(),
            'token_info': {
                'type': payload.get('token_type'),
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp'),
                'refresh_at': payload.get('refresh_at')
            }
        }
    }), 200
