#!/usr/bin/env python
"""
Test client for the 0xC Chat API.

This script demonstrates how to interact with the 0xC Chat API programmatically,
including user registration, login, sending messages, and retrieving messages.

Usage:
    python test_client.py

Requirements:
    - requests library: pip install requests
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime

class ChatAPIClient:
    """Client for interacting with the 0xC Chat API."""

    def __init__(self, base_url="http://localhost:5000", api_key=None):
        """Initialize the client with the API base URL and optional API key."""
        self.base_url = base_url
        self.api_key = api_key
        self.access_token = None
        self.refresh_token = None
        self.user_info = None
        self.refresh_at = None

    def _get_headers(self, include_auth=False):
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}

        # Add API key if provided
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        # Add authorization token if available and requested
        if include_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return headers

    def _handle_response(self, response):
        """Handle API response, checking for errors."""
        try:
            data = response.json()

            if response.status_code >= 400:
                print(f"Error: {data.get('message', 'Unknown error')}")
                return None

            return data
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON response - {response.text}")
            return None

    def register(self, username, password, email=None):
        """Register a new user."""
        print(f"\n=== Registering user: {username} ===")

        payload = {
            "username": username,
            "password": password
        }

        if email:
            payload["email"] = email

        response = requests.post(
            f"{self.base_url}/api/auth/register",
            headers=self._get_headers(),
            json=payload
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            print(f"User registered successfully: {username}")
            return True

        return False

    def login(self, username, password):
        """Login and get access and refresh tokens."""
        print(f"\n=== Logging in as: {username} ===")

        payload = {
            "username": username,
            "password": password
        }

        response = requests.post(
            f"{self.base_url}/api/auth/login",
            headers=self._get_headers(),
            json=payload
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            self.access_token = data["data"]["access_token"]
            self.refresh_token = data["data"]["refresh_token"]
            self.user_info = data["data"]["user"]

            # Get token info to know when to refresh
            self.get_token_info()

            print(f"Logged in successfully as: {username}")
            print(f"User ID: {self.user_info['id']}")
            return True

        return False

    def get_token_info(self):
        """Get information about the current token."""
        if not self.access_token:
            print("Error: Not logged in")
            return None

        response = requests.get(
            f"{self.base_url}/api/auth/token-info",
            headers=self._get_headers(include_auth=True)
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            token_info = data["data"]["token_info"]
            self.refresh_at = token_info.get("refresh_at")

            # Convert timestamps to readable format
            issued_at = datetime.fromtimestamp(token_info["issued_at"]).strftime('%Y-%m-%d %H:%M:%S')
            expires_at = datetime.fromtimestamp(token_info["expires_at"]).strftime('%Y-%m-%d %H:%M:%S')
            refresh_at = datetime.fromtimestamp(token_info["refresh_at"]).strftime('%Y-%m-%d %H:%M:%S')

            print(f"Token issued at: {issued_at}")
            print(f"Token expires at: {expires_at}")
            print(f"Token should be refreshed at: {refresh_at}")

            return token_info

        return None

    def refresh_token_if_needed(self):
        """Check if token needs refreshing and refresh if necessary."""
        if not self.refresh_at:
            return False

        current_time = int(time.time())
        if current_time >= self.refresh_at:
            print("\n=== Refreshing token ===")
            return self.refresh_access_token()

        return False

    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            print("Error: No refresh token available")
            return False

        payload = {
            "refresh_token": self.refresh_token
        }

        response = requests.post(
            f"{self.base_url}/api/auth/refresh",
            headers=self._get_headers(),
            json=payload
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            self.access_token = data["data"]["access_token"]
            print("Access token refreshed successfully")

            # Update token info
            self.get_token_info()
            return True

        return False

    def logout(self):
        """Logout and invalidate the refresh token."""
        if not self.refresh_token:
            print("Error: Not logged in")
            return False

        print("\n=== Logging out ===")

        payload = {
            "refresh_token": self.refresh_token
        }

        response = requests.post(
            f"{self.base_url}/api/auth/logout",
            headers=self._get_headers(),
            json=payload
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            self.access_token = None
            self.refresh_token = None
            self.user_info = None
            self.refresh_at = None
            print("Logged out successfully")
            return True

        return False

    def send_message(self, content, recipient_id=None):
        """Send a new message.

        Args:
            content: The content of the message
            recipient_id: Optional recipient user ID for private messages
        """
        if not self.access_token:
            print("Error: Not logged in")
            return None

        # Check if token needs refreshing
        self.refresh_token_if_needed()

        if recipient_id:
            print(f"\n=== Sending private message to user {recipient_id} ===")
        else:
            print(f"\n=== Sending public message ===")

        payload = {
            "content": content
        }

        if recipient_id:
            payload["recipient_id"] = recipient_id

        response = requests.post(
            f"{self.base_url}/api/messages",
            headers=self._get_headers(include_auth=True),
            json=payload
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            message = data["data"]
            print(f"Message sent: {message['id']}")
            return message

        return None

    def get_messages(self):
        """Get all messages."""
        if not self.access_token:
            print("Error: Not logged in")
            return []

        # Check if token needs refreshing
        self.refresh_token_if_needed()

        print("\n=== Getting all messages ===")

        response = requests.get(
            f"{self.base_url}/api/messages",
            headers=self._get_headers(include_auth=True)
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            messages = data["messages"]
            print(f"Retrieved {len(messages)} messages")
            return messages

        return []

    def get_my_messages(self):
        """Get messages by the authenticated user."""
        if not self.access_token:
            print("Error: Not logged in")
            return []

        # Check if token needs refreshing
        self.refresh_token_if_needed()

        print("\n=== Getting my messages ===")

        response = requests.get(
            f"{self.base_url}/api/messages/me",
            headers=self._get_headers(include_auth=True)
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            messages = data["messages"]
            print(f"Retrieved {len(messages)} of your messages")
            return messages

        return []

    def get_message(self, message_id):
        """Get a specific message by ID."""
        if not self.access_token:
            print("Error: Not logged in")
            return None

        # Check if token needs refreshing
        self.refresh_token_if_needed()

        print(f"\n=== Getting message: {message_id} ===")

        response = requests.get(
            f"{self.base_url}/api/messages/{message_id}",
            headers=self._get_headers(include_auth=True)
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            message = data["data"]
            print(f"Retrieved message: {message['id']}")
            return message

        return None

    def delete_message(self, message_id):
        """Delete a message by ID."""
        if not self.access_token:
            print("Error: Not logged in")
            return False

        # Check if token needs refreshing
        self.refresh_token_if_needed()

        print(f"\n=== Deleting message: {message_id} ===")

        response = requests.delete(
            f"{self.base_url}/api/messages/{message_id}",
            headers=self._get_headers(include_auth=True)
        )

        data = self._handle_response(response)
        if data and data.get("status") == "success":
            print(f"Message deleted: {message_id}")
            return True

        return False

    def print_message(self, message):
        """Print a message in a formatted way."""
        if not message:
            return

        print(f"ID: {message['id']}")
        print(f"From: {message['username']} ({message['user_id']})")
        print(f"Time: {message['timestamp']}")
        print(f"Content: {message['content']}")
        print("-" * 50)


def run_demo():
    """Run a demonstration of the client."""
    # Create client
    client = ChatAPIClient()

    # Dictionary to store user IDs
    user_ids = {}

    # Register three users
    client.register("testuser1", "password123", "test1@example.com")
    client.register("testuser2", "password123", "test2@example.com")
    client.register("testuser3", "password123", "test3@example.com")

    # Login as first user
    print("\n\n========== TESTING USER 1 ==========")
    if client.login("testuser1", "password123"):
        # Store user ID
        user_ids["testuser1"] = client.user_info["id"]

        # Send a public message
        public_message1 = client.send_message("Hello from testuser1! This is a public message.")

        # Get all messages
        all_messages = client.get_messages()
        print("\n=== All messages (as seen by User 1) ===")
        for message in all_messages:
            client.print_message(message)

        # Get my messages
        my_messages = client.get_my_messages()

        # Logout
        client.logout()

    # Login as second user
    print("\n\n========== TESTING USER 2 ==========")
    if client.login("testuser2", "password123"):
        # Store user ID
        user_ids["testuser2"] = client.user_info["id"]

        # Send a public message
        public_message2 = client.send_message("Hello from testuser2! This is a public message.")

        # Send a private message to user 1
        private_message2to1 = client.send_message(
            "Hello testuser1! This is a private message from testuser2.",
            user_ids["testuser1"]
        )

        # Get a specific message (public message from user 1)
        if public_message1:
            print("\n=== User 2 trying to access User 1's public message ===")
            specific_message = client.get_message(public_message1["id"])
            if specific_message:
                print("User 2 CAN access User 1's public message:")
                client.print_message(specific_message)
            else:
                print("User 2 CANNOT access User 1's public message or message not found")

        # Get all messages again
        all_messages = client.get_messages()
        print("\n=== All messages (as seen by User 2) ===")
        for message in all_messages:
            client.print_message(message)

        # Logout
        client.logout()

    # Login as third user
    print("\n\n========== TESTING USER 3 ==========")
    if client.login("testuser3", "password123"):
        # Store user ID
        user_ids["testuser3"] = client.user_info["id"]

        # Try to get user 1's public message
        if public_message1:
            print("\n=== User 3 trying to access User 1's public message ===")
            specific_message = client.get_message(public_message1["id"])
            if specific_message:
                print("User 3 CAN access User 1's public message:")
                client.print_message(specific_message)
            else:
                print("User 3 CANNOT access User 1's public message or message not found")

        # Try to get private message from user 2 to user 1
        if private_message2to1:
            print("\n=== User 3 trying to access private message from User 2 to User 1 ===")
            specific_message = client.get_message(private_message2to1["id"])
            if specific_message:
                print("User 3 CAN access the private message (security issue!):")
                client.print_message(specific_message)
            else:
                print("User 3 CANNOT access the private message (expected behavior)")

        # Send a private message to user 1
        private_message3to1 = client.send_message(
            "Hello testuser1! This is a private message from testuser3.",
            user_ids["testuser1"]
        )

        # Send a public message
        public_message3 = client.send_message("Hello from testuser3! This is a public message.")

        # Get all messages
        all_messages = client.get_messages()
        print("\n=== All messages (as seen by User 3) ===")
        for message in all_messages:
            client.print_message(message)

        # Logout
        client.logout()

    # Login as first user again to check private messages
    print("\n\n========== TESTING USER 1 AGAIN ==========")
    if client.login("testuser1", "password123"):
        # Get all messages
        all_messages = client.get_messages()
        print("\n=== All messages (as seen by User 1) ===")
        print(f"User 1 should see: public messages from all users + private messages sent to/from User 1")
        print(f"Expected count: 5 messages (3 public + 2 private to User 1)")
        print(f"Actual count: {len(all_messages)} messages")

        for message in all_messages:
            client.print_message(message)

        # Logout
        client.logout()

    print("\n\n========== TEST COMPLETE ==========")
    print("Privacy Model:")
    print("1. Public messages (no recipient_id) are visible to all users")
    print("2. Private messages (with recipient_id) are only visible to the sender and recipient")
    print("3. Each user can see: their own messages + messages sent to them + public messages")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test client for the 0xC Chat API")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL of the API")
    parser.add_argument("--api-key", help="API key for authentication (if SECRET_KEY_ENABLED=1)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Check if requests library is installed
    try:
        import requests
    except ImportError:
        print("Error: The requests library is required. Install it with 'pip install requests'")
        sys.exit(1)

    # Create client with command line arguments
    client = ChatAPIClient(base_url=args.url, api_key=args.api_key)

    # Run the demo
    run_demo()
