from flask import Flask, jsonify
from flask_cors import CORS
from routes import api
from auth_routes import auth
from config import config
import json_storage
from env import FLASK_ENV, API_PREFIX

def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = FLASK_ENV

    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize JSON storage
    json_storage.init_storage()

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(api, url_prefix=API_PREFIX)
    app.register_blueprint(auth, url_prefix=f'{API_PREFIX}/auth')

    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'name': '0xC Chat API',
            'version': '1.0.0',
            'description': 'A simple chat API built with Flask'
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

    return app

if __name__ == '__main__':
    from env import HOST, PORT, FLASK_ENV
    app = create_app()

    # Print startup message with port information
    print(f"\n🚀 0xC Chat API is starting up!")
    print(f"🔌 Server running at: http://{HOST if HOST != '0.0.0.0' else 'localhost'}:{PORT}")
    print(f"📚 API documentation available at: http://{HOST if HOST != '0.0.0.0' else 'localhost'}:{PORT}/")
    print(f"⚙️  Using environment: {FLASK_ENV}")
    print(f"🔍 Debug mode: {'enabled' if app.debug else 'disabled'}")
    print(f"💬 Press CTRL+C to quit\n")

    app.run(host=HOST, port=PORT)
