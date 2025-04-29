from datetime import datetime, timedelta, timezone
import uuid
import jwt
from passlib.hash import pbkdf2_sha256
import json_storage
from env import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRES, REFRESH_TOKEN_EXPIRES, TOKEN_REFRESH_SECONDS

class RefreshToken:
    """Refresh token model for storing valid refresh tokens."""

    def __init__(self, user_id, token=None, expires_days=REFRESH_TOKEN_EXPIRES):
        """Initialize a new refresh token."""
        self.id = token or str(uuid.uuid4())
        self.user_id = user_id
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self):
        """Convert token to dictionary for JSON storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Create a token instance from dictionary data."""
        token = cls(data['user_id'], data['id'])
        token.expires_at = datetime.fromisoformat(data['expires_at'])
        token.created_at = datetime.fromisoformat(data['created_at'])
        return token

    def is_expired(self):
        """Check if the token is expired."""
        return datetime.now(timezone.utc) > self.expires_at


class User:
    """User model for chat application."""

    def __init__(self, username, password, email=None):
        """Initialize a new user."""
        self.id = str(uuid.uuid4())
        self.username = username
        self.password_hash = pbkdf2_sha256.hash(password)
        self.email = email
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self):
        """Convert user to dictionary for JSON storage."""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Create a user instance from dictionary data."""
        user = cls.__new__(cls)  # Create instance without calling __init__
        user.id = data['id']
        user.username = data['username']
        user.password_hash = data['password_hash']
        user.email = data['email']
        user.created_at = datetime.fromisoformat(data['created_at'])
        return user

    def verify_password(self, password):
        """Verify password against stored hash."""
        return pbkdf2_sha256.verify(password, self.password_hash)

    def generate_access_token(self):
        """Generate a new access token for the user."""
        now = datetime.now(timezone.utc)
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': now + timedelta(minutes=ACCESS_TOKEN_EXPIRES),
            'iat': now,
            'token_type': 'access',
            'refresh_at': int((now + timedelta(seconds=TOKEN_REFRESH_SECONDS)).timestamp())
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

    def generate_refresh_token(self):
        """Generate a new refresh token for the user."""
        # Create a new refresh token
        token = RefreshToken(self.id)

        # Save to JSON storage
        token_dict = token.to_dict()
        json_storage.add_token(token_dict)

        return token.id

    @classmethod
    def register(cls, username, password, email=None):
        """Register a new user."""
        # Check if username already exists
        if cls.get_by_username(username):
            return None

        # Create new user
        user = User(username, password, email)

        # Save to JSON storage
        user_dict = user.to_dict()
        json_storage.add_user(user_dict)

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate a user by username and password."""
        user = cls.get_by_username(username)
        if user and user.verify_password(password):
            return user
        return None

    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID."""
        user_dict = json_storage.get_user_by_id(user_id)
        if user_dict:
            return cls.from_dict(user_dict)
        return None

    @classmethod
    def get_by_username(cls, username):
        """Get user by username."""
        user_dict = json_storage.get_user_by_username(username)
        if user_dict:
            return cls.from_dict(user_dict)
        return None

    @classmethod
    def get_by_refresh_token(cls, token_id):
        """Get user by refresh token."""
        # Find the token
        token_dict = json_storage.get_token_by_id(token_id)

        if token_dict:
            token = RefreshToken.from_dict(token_dict)

            # Check if token is expired
            if token.is_expired():
                # Remove expired token
                json_storage.delete_token(token_id)
                return None

            # Return the user
            return cls.get_by_id(token.user_id)

        return None

    @classmethod
    def invalidate_refresh_token(cls, token_id):
        """Invalidate a refresh token."""
        deleted_token = json_storage.delete_token(token_id)
        return deleted_token is not None

    @staticmethod
    def decode_token(token):
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}


class Message:
    """Message model for chat application."""

    def __init__(self, user_id, content):
        """Initialize a new message."""
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.content = content
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self):
        """Convert message to dictionary for JSON storage."""
        user = User.get_by_id(self.user_id)
        username = user.username if user else "Unknown"

        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': username,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Create a message instance from dictionary data."""
        message = cls.__new__(cls)  # Create instance without calling __init__
        message.id = data['id']
        message.user_id = data['user_id']
        message.content = data['content']
        message.timestamp = datetime.fromisoformat(data['timestamp'])
        return message

    @classmethod
    def get_all(cls):
        """Get all messages."""
        messages_dict = json_storage.get_messages()
        # Sort messages by timestamp
        messages_dict.sort(key=lambda x: x['timestamp'])
        return messages_dict

    @classmethod
    def get_by_user(cls, user_id):
        """Get all messages by a specific user."""
        messages_dict = json_storage.get_messages_by_user(user_id)
        # Sort messages by timestamp
        messages_dict.sort(key=lambda x: x['timestamp'])
        return messages_dict

    @classmethod
    def get_by_id(cls, message_id):
        """Get message by ID."""
        message_dict = json_storage.get_message_by_id(message_id)
        if message_dict:
            return cls.from_dict(message_dict)
        return None

    @classmethod
    def add(cls, user_id, content):
        """Add a new message."""
        message = Message(user_id, content)
        message_dict = message.to_dict()
        json_storage.add_message(message_dict)
        return message

    @classmethod
    def delete(cls, message_id, user_id=None):
        """Delete a message by ID, optionally checking user ownership."""
        deleted_message = json_storage.delete_message(message_id, user_id)
        if deleted_message:
            return cls.from_dict(deleted_message)
        return None
