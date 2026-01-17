"""
API documentation routes using Swagger
"""
from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

bp = Blueprint('docs', __name__)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "TuniGuard API",
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 3
    }
)

bp.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@bp.route('/api/swagger.json')
def swagger_spec():
    """Return Swagger/OpenAPI specification"""
    spec = {
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
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "tags": [
            {
                "name": "User Management",
                "description": "User registration and profile operations"
            },
            {
                "name": "Threat Detection",
                "description": "Core AI-powered threat scanning endpoints"
            },
            {
                "name": "Threat Intelligence",
                "description": "Threat catalog and trending scams"
            },
            {
                "name": "Chatbot",
                "description": "Interactive security assistant"
            },
            {
                "name": "Analytics",
                "description": "Statistics and performance metrics"
            }
        ],
        "paths": {},
        "definitions": {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    }
                }
            },
            "User": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "anonymized_id": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "risk_score": {"type": "number"},
                    "scan_count": {"type": "integer"}
                }
            },
            "ScanRequest": {
                "type": "object",
                "required": ["user_id", "content", "content_type"],
                "properties": {
                    "user_id": {"type": "integer"},
                    "content": {"type": "string"},
                    "content_type": {
                        "type": "string",
                        "enum": ["sms", "call", "app_message"]
                    },
                    "location_hint": {"type": "string"}
                }
            },
            "ScanResponse": {
                "type": "object",
                "properties": {
                    "scan_id": {"type": "integer"},
                    "threat_detected": {"type": "boolean"},
                    "detection_score": {"type": "number"},
                    "threat_type": {"type": "string"},
                    "severity": {"type": "string"},
                    "explanation": {"type": "string"},
                    "safe_actions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "intercept_time": {"type": "number"},
                    "timestamp": {"type": "string"}
                }
            }
        }
    }
    
    return jsonify(spec)
