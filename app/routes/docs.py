"""
API documentation routes using Swagger
Auto-generates documentation from route docstrings
"""
from flask import Blueprint
from flasgger import Flasgger

bp = Blueprint('docs', __name__)

def init_swagger(app):
    """Initialize Flasgger for auto-generated Swagger docs"""
    swagger = Flasgger(
        app,
        title='TuniGuard API',
        description='AI-Powered Telecommunications Security Sentinel for Tunisia\n\n'
                    'TuniGuard provides real-time threat detection for SMS, calls, and app messages using Google Gemini AI. '
                    'Protects against Tunisia-specific scams including fake telecom operators, mobile money fraud, and banking phishing.',
        version='1.0.0',
        uiversion=4,
        specs_route='/api/swagger.json',
        template={
            'swagger': '2.0',
            'info': {
                'title': 'TuniGuard API',
                'version': '1.0.0',
                'contact': {
                    'name': 'TuniGuard Team',
                    'url': 'https://tuniguard.tn'
                },
                'license': {
                    'name': 'MIT',
                    'url': 'https://opensource.org/licenses/MIT'
                }
            },
            'host': 'localhost:5000',
            'basePath': '/api',
            'schemes': ['http', 'https'],
            'consumes': ['application/json'],
            'produces': ['application/json'],
            'securityDefinitions': {
                'Bearer': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header',
                    'description': 'JWT Bearer token. Format: Bearer <token>'
                }
            },
            'tags': [
                {
                    'name': 'User Management',
                    'description': 'User registration and profile operations'
                },
                {
                    'name': 'Threat Detection',
                    'description': 'Core AI-powered threat scanning endpoints'
                },
                {
                    'name': 'Threat Intelligence',
                    'description': 'Threat catalog and trending scams'
                },
                {
                    'name': 'Chat',
                    'description': 'Interactive security chatbot'
                },
                {
                    'name': 'Analytics',
                    'description': 'Statistics and performance metrics'
                }
            ],
            'definitions': {
                'Error': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'description': 'Error message'
                        },
                        'details': {
                            'type': 'string',
                            'description': 'Additional error details'
                        }
                    }
                },
                'User': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'integer'},
                        'username': {'type': 'string'},
                        'anonymized_id': {'type': 'string'},
                        'created_at': {'type': 'string', 'format': 'date-time'},
                        'risk_score': {'type': 'number'},
                        'scan_count': {'type': 'integer'},
                        'region': {'type': 'string'},
                        'carrier': {'type': 'string'}
                    }
                },
                'Threat': {
                    'type': 'object',
                    'properties': {
                        'threat_id': {'type': 'integer'},
                        'type': {'type': 'string'},
                        'category': {'type': 'string', 'enum': ['SMS', 'Call', 'App Message']},
                        'severity': {'type': 'string', 'enum': ['Low', 'Medium', 'High', 'Critical']},
                        'description': {'type': 'string'},
                        'signature': {'type': 'string'},
                        'detection_count': {'type': 'integer'}
                    }
                },
                'Scan': {
                    'type': 'object',
                    'properties': {
                        'scan_id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'threat_id': {'type': 'integer'},
                        'input_text': {'type': 'string'},
                        'content_type': {'type': 'string'},
                        'detection_score': {'type': 'number'},
                        'gemini_response': {'type': 'string'},
                        'timestamp': {'type': 'string', 'format': 'date-time'},
                        'intercept_time': {'type': 'number'},
                        'user_action': {'type': 'string'},
                        'location_hint': {'type': 'string'}
                    }
                },
                'Conversation': {
                    'type': 'object',
                    'properties': {
                        'conv_id': {'type': 'integer'},
                        'scan_id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'role': {'type': 'string', 'enum': ['user', 'assistant']},
                        'timestamp': {'type': 'string', 'format': 'date-time'}
                    }
                },
                'ThreatIntel': {
                    'type': 'object',
                    'properties': {
                        'intel_id': {'type': 'integer'},
                        'threat_id': {'type': 'integer'},
                        'reported_date': {'type': 'string', 'format': 'date-time'},
                        'source_region': {'type': 'string'},
                        'frequency': {'type': 'integer'},
                        'trend_score': {'type': 'number'},
                        'escalation_level': {'type': 'string'},
                        'mitigation_status': {'type': 'string'}
                    }
                }
            }
        }
    )
    
    return swagger
