"""
TuniGuard Flask Application Factory
Initializes the Flask app with all extensions and configurations
"""
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flasgger import Swagger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Initialize Flasgger (Swagger UI)
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/api/swagger.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "TuniGuard API",
            "description": "AI-Powered Telecommunications Security Sentinel for Tunisia\n\n"
                          "TuniGuard provides real-time threat detection for SMS, calls, and app messages using Google Gemini AI. "
                          "Protects against Tunisia-specific scams including fake telecom operators, mobile money fraud, and banking phishing.",
            "version": "1.0.0",
            "contact": {
                "name": "TuniGuard Team",
                "url": "https://tuniguard.tn"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "host": "localhost:5000",
        "basePath": "/api",
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register blueprints
    from app.routes import auth, threats, scans, analytics, chat
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(threats.bp)
    app.register_blueprint(scans.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(chat.bp)
    
    # Serve static files and templates
    @app.route('/')
    def index():
        """Serve the main frontend page"""
        return render_template('index.html')
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """API health status"""
        return jsonify({
            'status': 'online',
            'service': 'TuniGuard API',
            'version': '1.0.0',
            'message': 'Protecting Tunisia\'s digital communications'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(error)}), 500
    
    @app.before_request
    def before_request_logging():
        import sys
        print(f"[REQUEST] {request.method} {request.path}", file=sys.stderr)
        sys.stderr.flush()
    
    return app
