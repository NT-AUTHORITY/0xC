"""
Environment variables for the 0xC Chat application.
This file defines default environment variables that can be overridden
by setting actual environment variables or using a .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Application environment
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
FLASK_APP = os.environ.get('FLASK_APP', 'app.py')

# Server configuration
# HOST: The IP address the server will listen on
# - 0.0.0.0: Listen on all available network interfaces (default)
# - 127.0.0.1: Listen only on localhost (more secure for development)
HOST = os.environ.get('HOST', '0.0.0.0')

# PORT: The port number the server will listen on
# - Can be customized by setting the PORT environment variable
# - Example: PORT=8080 python app.py
# - Default: 5000
PORT = int(os.environ.get('PORT', 5000))

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-0xC-chat')

# SECRET_KEY_ENABLED: If true, all API operations require a secret key
# - This adds an additional layer of security beyond user authentication
# - When enabled, all requests must include X-API-Key header with SECRET_KEY
# - Default: False (disabled)
SECRET_KEY_ENABLED = os.environ.get('SECRET_KEY_ENABLED', '0') == '1'

# Authentication
# JWT_SECRET_KEY: Secret key used for JWT token signing
# - Should be different from the main SECRET_KEY for better security
# - Default is a placeholder, should be changed in production
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-for-0xC-chat')

# REGISTER_ENABLED: If false, user registration is disabled
# - Useful for production environments where you want to control user creation
# - When disabled, the /api/auth/register endpoint will return a 403 error
# - Default: True (enabled)
REGISTER_ENABLED = os.environ.get('REGISTER_ENABLED', '1') == '1'

# ACCESS_TOKEN_EXPIRES: Time in minutes before access tokens expire
# - Default: 15 minutes
ACCESS_TOKEN_EXPIRES = int(os.environ.get('ACCESS_TOKEN_EXPIRES', 15))

# TOKEN_REFRESH_SECONDS: Time in seconds before a token should be refreshed
# - This is different from expiration - it indicates when a client should proactively refresh
# - Default: 600 seconds (10 minutes)
# - Should be less than ACCESS_TOKEN_EXPIRES to allow time for refresh
TOKEN_REFRESH_SECONDS = int(os.environ.get('TOKEN_REFRESH_SECONDS', 600))

# REFRESH_TOKEN_EXPIRES: Time in days before refresh tokens expire
# - Default: 30 days
REFRESH_TOKEN_EXPIRES = int(os.environ.get('REFRESH_TOKEN_EXPIRES', 30))

# API configuration
API_PREFIX = os.environ.get('API_PREFIX', '/api')

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Data storage configuration
# DATA_DIR: Directory where JSON data files will be stored
# - Default: 'data' directory in the project root
DATA_DIR = os.environ.get('DATA_DIR', 'data')

# CORS settings
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# Rate limiting
RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', '0') == '1'
RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 100))  # requests per minute

# Message configuration
MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', 1000))
