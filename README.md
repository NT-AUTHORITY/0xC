# 0xC Chat API

A simple chat API built with Python Flask for the 0xC (Chat) project.

[中文文档](README_ZH.md)

## Features

- RESTful API for chat messages
- Create, read, and delete operations for messages
- User authentication with JWT tokens and refresh tokens
- JSON file storage for persistent data
- JSON responses
- Configurable via environment variables (customizable port, host, etc.)

## Project Structure

```
0xC/
├── app.py              # Main application file
├── auth.py             # Authentication middleware
├── api_key.py          # API Key middleware
├── auth_routes.py      # Authentication routes
├── config.py           # Configuration settings
├── env.py              # Environment variables
├── json_storage.py     # JSON file storage module
├── models.py           # Data models
├── routes.py           # API routes
├── requirements.txt    # Dependencies
├── test_api.py         # Unit tests
├── test_client.py      # Sample client for API testing
├── .env.example        # Example environment variables
├── data/               # Directory for JSON data files (created at runtime)
│   ├── users.json      # User data
│   ├── messages.json   # Message data
│   └── tokens.json     # Refresh token data
├── README.md           # English documentation
└── README_ZH.md        # Chinese documentation
```

## API Endpoints

### Message Endpoints

- `GET /api/messages` - Retrieve all messages viewable by the current user (requires authentication)
- `POST /api/messages` - Send a new message, optionally to a specific recipient (requires authentication)
- `GET /api/messages/<message_id>` - Get a specific message (requires authentication and permission)
- `DELETE /api/messages/<message_id>` - Delete a message (requires authentication and ownership)
- `GET /api/messages/me` - Get all messages sent by the authenticated user (requires authentication)

Note: A user can view messages if they are:
1. The sender of the message
2. The recipient of the message
3. The message is public (no recipient specified)

### Authentication Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access and refresh tokens
- `POST /api/auth/refresh` - Refresh access token using refresh token
- `POST /api/auth/logout` - Logout and invalidate refresh token
- `GET /api/auth/token-info` - Get information about the current token

## API Security Mechanisms

### API Key Authentication

When `SECRET_KEY_ENABLED=1`, all API requests must include an API Key in the header:

```
X-API-Key: your-secret-key-here
```

This is a global security mechanism, independent of the user authentication system. It can be used to:
- Restrict API access to authorized client applications only
- Add an extra layer of security for the entire API
- Disable in development or testing environments (set `SECRET_KEY_ENABLED=0`)

### JWT Authentication

JWT (JSON Web Token) is used for user-level authentication and authorization:
- Users receive access tokens and refresh tokens after logging in
- Access tokens are used to access protected API endpoints
- Refresh tokens are used to obtain new access tokens when they expire

Both authentication mechanisms can be used simultaneously to provide multi-layered security protection.

## API Response Format

All API responses follow a consistent JSON format with the following fields:

### Success Responses

Success responses contain a `status` field (with value "success") and related data:

```json
{
  "status": "success",
  "message": "Description of the successful operation (optional)",
  "data": {
    // Data object (for single resource)
  }
}
```

Or for endpoints returning collections:

```json
{
  "status": "success",
  "messages": [
    // Array of data objects
  ]
}
```

### Error Responses

Error responses contain a `status` field (with value "error") and an error message:

```json
{
  "status": "error",
  "message": "Error description"
}
```

#### Error Response Examples

**Authentication Failure (401 Unauthorized)**:

```json
{
  "status": "error",
  "message": "Authentication token is missing"
}
```

**Resource Not Found (404 Not Found)**:

```json
{
  "status": "error",
  "message": "Message with ID 550e8400-e29b-41d4-a716-446655440001 not found"
}
```

**Invalid Request Parameters (400 Bad Request)**:

```json
{
  "status": "error",
  "message": "Missing required field: content"
}
```

**Permission Error (401 Unauthorized)**:

```json
{
  "status": "error",
  "message": "Message with ID 550e8400-e29b-41d4-a716-446655440001 not found or you do not have permission to delete it"
}
```

### HTTP Status Codes

The API uses standard HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication failed or missing
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

## Authentication Flow

The 0xC Chat API uses a JWT-based authentication system, including Access Tokens and Refresh Tokens.

### Authentication Flow Diagram

```
┌─────────┐                                                  ┌─────────┐
│         │                                                  │         │
│  Client │                                                  │  Server │
│         │                                                  │         │
└────┬────┘                                                  └────┬────┘
     │                                                            │
     │  1. Register user POST /api/auth/register                  │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  2. Return user information                                │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  3. Login POST /api/auth/login                             │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  4. Return access token and refresh token                  │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  5. Access protected resources with access token           │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  6. Return protected resources                             │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  7. Access token expires                                   │
     │                                                            │
     │  8. Get new access token using refresh token               │
     │    POST /api/auth/refresh                                  │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  9. Return new access token                                │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  10. Access protected resources with new access token      │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  11. Return protected resources                            │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
     │  12. Logout POST /api/auth/logout                          │
     │ ─────────────────────────────────────────────────────────> │
     │                                                            │
     │  13. Confirm successful logout                             │
     │ <───────────────────────────────────────────────────────── │
     │                                                            │
```

### Authentication Details

1. **Access Token**:
   - Short-lived (default: 15 minutes)
   - Used to access protected API endpoints
   - Included in request headers as `Authorization: Bearer <token>`
   - Contains a `refresh_at` timestamp indicating when the client should refresh the token (default: 10 minutes before expiration)

2. **Refresh Token**:
   - Long-lived (default: 30 days)
   - Used to obtain new access tokens when they expire
   - Stored on the client side and must be kept secure

3. **Authentication Process**:
   - User registers and logs in to receive tokens
   - Access token is used to access protected resources
   - When the current time reaches the `refresh_at` timestamp, the client should proactively refresh the token (before it completely expires)
   - If the access token has expired, the refresh token is used to obtain a new access token
   - Continue using the new access token to access protected resources
   - When the user logs out, the refresh token is invalidated on the server side

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/NT_AUTHORITY/0xC.git
   cd 0xC
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables (optional):
   ```
   cp .env.example .env
   # Edit .env file with your preferred settings
   ```

5. Run the application:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000` by default, or at the host and port specified in your environment variables.

### Customizing the Port

You can run the application on a different port in several ways:

1. **Using environment variables directly**:
   ```bash
   # On Linux/Mac
   PORT=8080 python app.py

   # On Windows (PowerShell)
   $env:PORT=8080; python app.py

   # On Windows (Command Prompt)
   set PORT=8080 && python app.py
   ```

2. **Using a .env file**:
   Create or edit your `.env` file and add:
   ```
   PORT=8080
   ```
   Then run the application normally:
   ```
   python app.py
   ```

The application will now be available at `http://localhost:8080`.

## Testing

### Unit Tests

Run the unit tests using:
```
python test_api.py
```

### Test Client

A sample client is provided to demonstrate how to interact with the API programmatically:

```
python test_client.py
```

The test client demonstrates:
- User registration and login
- Token management (including automatic token refresh)
- Sending and retrieving messages
- Error handling

You can customize the API URL and provide an API key using command-line arguments:

```
python test_client.py --url http://localhost:8080 --api-key your-secret-key
```

Requirements:
- The `requests` library: `pip install requests`

## Example Usage

### Authentication

#### Register a new user

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"username": "user1", "password": "password123", "email": "user1@example.com"}'
```

> Note: The `X-API-Key` header is only required when `SECRET_KEY_ENABLED=1`

**Response:**

```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "user1",
    "email": "user1@example.com",
    "created_at": "2023-09-15T14:30:45.123456"
  }
}
```

#### Login and get tokens

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```

**Response:**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "email": "user1@example.com",
      "created_at": "2023-09-15T14:30:45.123456"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

#### Refresh access token

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

**Response:**

```json
{
  "status": "success",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

#### Logout

```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

**Response:**

```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

#### Token Info

```bash
curl -X GET http://localhost:5000/api/auth/token-info \
  -H "Authorization: Bearer your-access-token"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "email": "user1@example.com",
      "created_at": "2023-09-15T14:30:45.123456"
    },
    "token_info": {
      "type": "access",
      "issued_at": 1694789445,
      "expires_at": 1694790345,
      "refresh_at": 1694790045
    }
  }
}
```

### Messages

#### Send a public message (authenticated)

```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"content": "Hello, world!"}'
```

#### Send a private message to a specific user (authenticated)

```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -H "X-API-Key: your-secret-key-here" \
  -d '{"content": "Hello, this is a private message!", "recipient_id": "user-id-here"}'
```

> Note:
> - The `Authorization` header is used for user authentication (JWT)
> - The `X-API-Key` header is used for API authentication (only required when `SECRET_KEY_ENABLED=1`)
> - Public messages (without recipient_id) are visible to all users
> - Private messages (with recipient_id) are only visible to the sender and recipient

**Response:**

```json
{
  "status": "success",
  "message": "Message created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "user1",
    "content": "Hello, world!",
    "timestamp": "2023-09-15T14:35:12.654321"
  }
}
```

#### Get your messages (authenticated)

```bash
curl -X GET http://localhost:5000/api/messages \
  -H "Authorization: Bearer your-access-token"
```

**Response:**

```json
{
  "status": "success",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "content": "Hello, world!",
      "timestamp": "2023-09-15T14:35:12.654321"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440003",
      "username": "user2",
      "content": "Hi there!",
      "timestamp": "2023-09-15T14:36:05.123456"
    }
  ]
}
```

#### Get my messages (authenticated)

```bash
curl -X GET http://localhost:5000/api/messages/me \
  -H "Authorization: Bearer your-access-token"
```

**Response:**

```json
{
  "status": "success",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "user1",
      "content": "Hello, world!",
      "timestamp": "2023-09-15T14:35:12.654321"
    }
  ]
}
```

#### Get a specific message (authenticated, ownership required)

```bash
curl -X GET http://localhost:5000/api/messages/550e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer your-access-token"
```

Note: This will only succeed if the authenticated user is the sender of the message.

**Response:**

```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "user1",
    "content": "Hello, world!",
    "timestamp": "2023-09-15T14:35:12.654321"
  }
}
```

#### Delete a message (authenticated, ownership required)

```bash
curl -X DELETE http://localhost:5000/api/messages/550e8400-e29b-41d4-a716-446655440001 \
  -H "Authorization: Bearer your-access-token"
```

**Response:**

```json
{
  "status": "success",
  "message": "Message with ID 550e8400-e29b-41d4-a716-446655440001 deleted successfully"
}
```

## Environment Variables

The application uses environment variables for configuration. You can set these in a `.env` file or directly in your environment.

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_ENV | Application environment | development |
| FLASK_DEBUG | Enable debug mode | 1 (True) |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 5000 |
| SECRET_KEY | Secret key for security | dev-key-for-0xC-chat |
| SECRET_KEY_ENABLED | If true, all API operations require a secret key (X-API-Key header) | 0 (False) |
| JWT_SECRET_KEY | Secret key for JWT tokens (used to sign and verify user authentication tokens) | jwt-secret-key-for-0xC-chat |
| REGISTER_ENABLED | If false, user registration is disabled | 1 (True) |
| ACCESS_TOKEN_EXPIRES | Time in minutes before access tokens expire | 15 |
| TOKEN_REFRESH_SECONDS | Time in seconds before a token should be refreshed | 600 |
| REFRESH_TOKEN_EXPIRES | Time in days before refresh tokens expire | 30 |
| API_PREFIX | API endpoint prefix | /api |
| LOG_LEVEL | Logging level | INFO |
| DATA_DIR | Directory where JSON data files will be stored | data |
| CORS_ORIGINS | Allowed CORS origins | * |
| RATE_LIMIT_ENABLED | Enable rate limiting | 0 (False) |
| RATE_LIMIT | Rate limit per minute | 100 |
| MAX_MESSAGE_LENGTH | Maximum message length | 1000 |

## Future Improvements

- Implement chat rooms or direct messaging between users
- Add message editing functionality
- Implement real-time messaging with WebSockets
- Add user profile management
- Add password reset functionality
- Implement role-based access control
- Add email verification
- Implement rate limiting for authentication endpoints
- Add database support as an alternative storage option
