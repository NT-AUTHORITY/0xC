"""
JSON storage module for the 0xC Chat application.

This module provides functions to read and write data to JSON files,
serving as a simple persistence layer for the application.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from env import DATA_DIR

# File paths for JSON storage
USERS_FILE = os.path.join(DATA_DIR, "users.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
TOKENS_FILE = os.path.join(DATA_DIR, "tokens.json")

# Initialize empty data structures if files don't exist
def init_storage():
    """Initialize the JSON storage files if they don't exist."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'w') as f:
            json.dump([], f)

# User storage functions
def get_users() -> List[Dict[str, Any]]:
    """Get all users from the JSON file."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, initialize it
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
        return []

def save_users(users: List[Dict[str, Any]]) -> None:
    """Save users to the JSON file."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    users = get_users()
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get a user by username."""
    users = get_users()
    for user in users:
        if user['username'] == username:
            return user
    return None

def add_user(user: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new user."""
    users = get_users()
    users.append(user)
    save_users(users)
    return user

def update_user(user_id: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a user's data."""
    users = get_users()
    for i, user in enumerate(users):
        if user['id'] == user_id:
            users[i].update(updated_data)
            save_users(users)
            return users[i]
    return None

# Message storage functions
def get_messages() -> List[Dict[str, Any]]:
    """Get all messages from the JSON file."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, initialize it
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)
        return []

def save_messages(messages: List[Dict[str, Any]]) -> None:
    """Save messages to the JSON file."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def get_message_by_id(message_id: str) -> Optional[Dict[str, Any]]:
    """Get a message by ID."""
    messages = get_messages()
    for message in messages:
        if message['id'] == message_id:
            return message
    return None

def get_messages_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Get all messages by a specific user."""
    messages = get_messages()
    return [message for message in messages if message['user_id'] == user_id]

def add_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new message."""
    messages = get_messages()
    messages.append(message)
    save_messages(messages)
    return message

def delete_message(message_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Delete a message by ID, optionally checking user ownership."""
    messages = get_messages()
    for i, message in enumerate(messages):
        if message['id'] == message_id:
            # If user_id is provided, check ownership
            if user_id and message['user_id'] != user_id:
                return None
            deleted_message = messages.pop(i)
            save_messages(messages)
            return deleted_message
    return None

# Token storage functions
def get_tokens() -> List[Dict[str, Any]]:
    """Get all refresh tokens from the JSON file."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, initialize it
        with open(TOKENS_FILE, 'w') as f:
            json.dump([], f)
        return []

def save_tokens(tokens: List[Dict[str, Any]]) -> None:
    """Save refresh tokens to the JSON file."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

def get_token_by_id(token_id: str) -> Optional[Dict[str, Any]]:
    """Get a refresh token by ID."""
    tokens = get_tokens()
    for token in tokens:
        if token['id'] == token_id:
            return token
    return None

def add_token(token: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new refresh token."""
    tokens = get_tokens()
    tokens.append(token)
    save_tokens(tokens)
    return token

def delete_token(token_id: str) -> Optional[Dict[str, Any]]:
    """Delete a refresh token by ID."""
    tokens = get_tokens()
    for i, token in enumerate(tokens):
        if token['id'] == token_id:
            deleted_token = tokens.pop(i)
            save_tokens(tokens)
            return deleted_token
    return None

# Initialize storage on module import
init_storage()
