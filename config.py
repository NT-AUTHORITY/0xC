from env import (
    SECRET_KEY, HOST, PORT, API_PREFIX,
    LOG_LEVEL, CORS_ORIGINS, RATE_LIMIT_ENABLED, RATE_LIMIT,
    MAX_MESSAGE_LENGTH
)

class Config:
    """Base configuration."""
    SECRET_KEY = SECRET_KEY
    DEBUG = False
    TESTING = False
    HOST = HOST
    PORT = PORT
    API_PREFIX = API_PREFIX
    LOG_LEVEL = LOG_LEVEL
    CORS_ORIGINS = CORS_ORIGINS
    RATE_LIMIT_ENABLED = RATE_LIMIT_ENABLED
    RATE_LIMIT = RATE_LIMIT
    MAX_MESSAGE_LENGTH = MAX_MESSAGE_LENGTH

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Dictionary with different configuration environments
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
