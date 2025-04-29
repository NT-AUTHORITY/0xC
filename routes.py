from flask import Blueprint, request, jsonify
from models import Message, User
from env import MAX_MESSAGE_LENGTH
from auth import token_required
from api_key import api_key_required

# Create a Blueprint for the API routes
api = Blueprint('api', __name__)

@api.route('/messages', methods=['GET'])
@api_key_required
def get_messages():
    """Get all messages (public endpoint, requires API key if enabled)."""
    return jsonify({
        'status': 'success',
        'messages': Message.get_all()
    }), 200

@api.route('/messages', methods=['POST'])
@api_key_required
@token_required
def create_message(current_user):
    """Create a new message (requires authentication)."""
    data = request.get_json()

    # Validate request data
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No input data provided'
        }), 400

    # Check required fields
    if 'content' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required field: content'
        }), 400

    # Validate message length
    if len(data['content']) > MAX_MESSAGE_LENGTH:
        return jsonify({
            'status': 'error',
            'message': f'Message content exceeds maximum length of {MAX_MESSAGE_LENGTH} characters'
        }), 400

    # Create new message with authenticated user's ID
    message = Message.add(current_user.id, data['content'])

    return jsonify({
        'status': 'success',
        'message': 'Message created successfully',
        'data': message.to_dict()
    }), 201

@api.route('/messages/<message_id>', methods=['GET'])
@api_key_required
def get_message(message_id):
    """Get a specific message by ID (public endpoint, requires API key if enabled)."""
    message = Message.get_by_id(message_id)

    if not message:
        return jsonify({
            'status': 'error',
            'message': f'Message with ID {message_id} not found'
        }), 404

    return jsonify({
        'status': 'success',
        'data': message.to_dict()
    }), 200

@api.route('/messages/<message_id>', methods=['DELETE'])
@api_key_required
@token_required
def delete_message(current_user, message_id):
    """Delete a message by ID (requires authentication and ownership)."""
    # Delete message, checking ownership
    message = Message.delete(message_id, current_user.id)

    if not message:
        return jsonify({
            'status': 'error',
            'message': f'Message with ID {message_id} not found or you do not have permission to delete it'
        }), 404

    return jsonify({
        'status': 'success',
        'message': f'Message with ID {message_id} deleted successfully'
    }), 200

@api.route('/messages/me', methods=['GET'])
@api_key_required
@token_required
def get_my_messages(current_user):
    """Get all messages by the authenticated user."""
    return jsonify({
        'status': 'success',
        'messages': Message.get_by_user(current_user.id)
    }), 200
