"""
Utility functions for TuniGuard
"""
import random
import string
import time
from datetime import datetime
from functools import wraps
from flask import request, jsonify, current_app
from app import db
from app.models import APIMetric

def generate_anonymized_id(prefix='TG'):
    """Generate anonymized user ID (e.g., TG-A7B9C2)"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{random_part}"

def simulate_intercept_time():
    """Simulate telecom network routing delay (200-400ms)"""
    return round(random.uniform(200, 400), 2)

def calculate_risk_score(scan_history):
    """
    Calculate user risk score based on scan history
    
    Args:
        scan_history: List of previous scans
    
    Returns:
        float: Risk score 0-100
    """
    if not scan_history:
        return 50.0  # Neutral score
    
    total_scans = len(scan_history)
    high_risk_scans = sum(1 for scan in scan_history if scan.detection_score > 70)
    
    # Higher interaction = better awareness = lower risk
    engagement_factor = min(total_scans / 10, 1.0)  # Cap at 10 scans
    threat_exposure = (high_risk_scans / total_scans) if total_scans > 0 else 0
    
    # Lower score = better security posture
    risk_score = 100 - (engagement_factor * 50) + (threat_exposure * 30)
    
    return round(max(0, min(100, risk_score)), 2)

def get_threat_signal_bars(score):
    """Convert threat score to signal bar visualization"""
    if score < 25:
        return "░░░░░ (Weak Signal - Low Risk)"
    elif score < 50:
        return "██░░░ (Moderate Signal - Medium Risk)"
    elif score < 75:
        return "████░ (Strong Signal - High Risk)"
    else:
        return "█████ (Critical Interference - Extreme Risk)"

def log_api_metric(endpoint):
    """Decorator to log API performance metrics"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            response = f(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Determine status code
            if isinstance(response, tuple):
                status_code = response[1]
            else:
                status_code = 200
            
            # Log to database
            try:
                metric = APIMetric(
                    endpoint=endpoint,
                    response_time=round(response_time, 2),
                    status_code=status_code,
                    timestamp=datetime.utcnow()
                )
                db.session.add(metric)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to log metric: {str(e)}")
            
            return response
        return decorated_function
    return decorator

def validate_request_data(schema):
    """Decorator for request validation using Marshmallow"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = schema.validate(request.get_json())
            if errors:
                return jsonify({'error': 'Validation failed', 'details': errors}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(text, max_length=5000):
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Remove HTML tags
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limit length
    text = text[:max_length]
    
    # Strip excessive whitespace
    text = ' '.join(text.split())
    
    return text

def get_region_from_hint(location_hint):
    """Map location hints to Tunisian regions"""
    regions = {
        'tunis': 'Greater Tunis',
        'sfax': 'Sfax Region',
        'sousse': 'Sousse-Monastir',
        'ariana': 'Greater Tunis',
        'ben arous': 'Greater Tunis',
        'manouba': 'Greater Tunis',
        'nabeul': 'Cap Bon',
        'bizerte': 'Bizerte Region',
        'gabes': 'South Tunisia',
        'medenine': 'South Tunisia',
        'gafsa': 'South Tunisia',
        'kairouan': 'Central Tunisia',
        'kasserine': 'Central Tunisia',
        'sidi bouzid': 'Central Tunisia',
    }
    
    if not location_hint:
        return 'Tunisia'
    
    location_lower = location_hint.lower()
    for key, region in regions.items():
        if key in location_lower:
            return region
    
    return 'Tunisia'
