from flask import Blueprint, request, jsonify
from models import Message, User
from env import MAX_MESSAGE_LENGTH
from auth import token_required
from api_key import api_key_required

# Create a Blueprint for the API routes
api = Blueprint('api', __name__)

@api.route('/messages', methods=['GET'])
@api_key_required
@token_required
def get_messages(current_user):
    """Get all messages viewable by the current user (requires authentication).

    This includes:
    1. Messages sent by the user
    2. Messages sent to the user
    3. Public messages (no recipient specified)
    """
    return jsonify({
        'status': 'success',
        'messages': Message.get_viewable_by_user(current_user.id)
    }), 200

@api.route('/messages', methods=['POST'])
@api_key_required
@token_required
def create_message(current_user):
    """Create a new message (requires authentication).

    Request body:
    {
        "content": "Message content",
        "recipient_id": "optional-user-id-for-private-message"
    }

    If recipient_id is provided, the message will only be visible to the sender and recipient.
    If recipient_id is not provided, the message will be public (visible to all users).
    """
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

    # Get recipient_id if provided
    recipient_id = data.get('recipient_id')

    # Validate recipient_id if provided
    if recipient_id:
        recipient = User.get_by_id(recipient_id)
        if not recipient:
            return jsonify({
                'status': 'error',
                'message': f'Recipient with ID {recipient_id} not found'
            }), 404

    # Create new message with authenticated user's ID and optional recipient_id
    message = Message.add(current_user.id, data['content'], recipient_id)

    return jsonify({
        'status': 'success',
        'message': 'Message created successfully',
        'data': message.to_dict()
    }), 201

@api.route('/messages/<message_id>', methods=['GET'])
@api_key_required
@token_required
def get_message(current_user, message_id):
    """Get a specific message by ID (requires authentication).

    A user can view a message if they are:
    1. The sender of the message
    2. The recipient of the message
    3. The message is public (no recipient specified)
    """
    message = Message.get_by_id(message_id)

    if not message:
        return jsonify({
            'status': 'error',
            'message': f'Message with ID {message_id} not found'
        }), 404

    # Check if the current user has permission to view the message
    can_view = False

    # User is the sender
    if message.user_id == current_user.id:
        can_view = True
    # User is the recipient
    elif message.recipient_id == current_user.id:
        can_view = True
    # Message is public (no recipient)
    elif message.recipient_id is None:
        can_view = True

    if not can_view:
        return jsonify({
            'status': 'error',
            'message': f'Message with ID {message_id} not found or you do not have permission to view it'
        }), 403

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
