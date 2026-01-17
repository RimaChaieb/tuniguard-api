"""
Threat catalog and intelligence routes
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Threat, ThreatIntel, Scan
from app.models.schemas import ThreatSchema
from app.utils.helpers import log_api_metric
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('threats', __name__, url_prefix='/api')
threat_schema = ThreatSchema()
threats_schema = ThreatSchema(many=True)

@bp.route('/threats', methods=['GET'])
@log_api_metric('/api/threats')
def get_threats():
    """
    List all known threat categories
    ---
    tags:
      - Threat Intelligence
    parameters:
      - in: query
        name: category
        type: string
        description: Filter by category (SMS, Call, App Message)
      - in: query
        name: severity
        type: string
        description: Filter by severity (Low, Medium, High, Critical)
    responses:
      200:
        description: List of threats
        schema:
          type: array
          items:
            properties:
              threat_id:
                type: integer
              type:
                type: string
              category:
                type: string
              severity:
                type: string
              description:
                type: string
              detection_count:
                type: integer
    """
    query = Threat.query
    
    # Apply filters
    category = request.args.get('category')
    severity = request.args.get('severity')
    
    if category:
        query = query.filter_by(category=category)
    if severity:
        query = query.filter_by(severity=severity)
    
    threats = query.all()
    
    # Convert to dict format
    threat_list = [{
        'threat_id': t.threat_id,
        'type': t.type,
        'category': t.category,
        'severity': t.severity,
        'description': t.description,
        'detection_count': t.detection_count
    } for t in threats]
    
    return jsonify({
        'total': len(threats),
        'threats': threat_list
    }), 200

@bp.route('/threats/<int:threat_id>', methods=['GET'])
@log_api_metric('/api/threats/detail')
def get_threat_detail(threat_id):
    """
    Get detailed information about a specific threat
    ---
    tags:
      - Threat Intelligence
    parameters:
      - in: path
        name: threat_id
        type: integer
        required: true
    responses:
      200:
        description: Threat details
      404:
        description: Threat not found
    """
    threat = Threat.query.get(threat_id)
    
    if not threat:
        return jsonify({'error': 'Threat not found'}), 404
    
    # Get recent detections
    recent_scans = Scan.query.filter_by(threat_id=threat_id)\
        .order_by(Scan.timestamp.desc())\
        .limit(10)\
        .all()
    
    return jsonify({
        **threat_schema.dump(threat),
        'recent_detections': len(recent_scans),
        'last_detected': recent_scans[0].timestamp.isoformat() if recent_scans else None
    }), 200

@bp.route('/threats/trending', methods=['GET'])
@log_api_metric('/api/threats/trending')
def get_trending_threats():
    """
    Get current high-frequency scams
    ---
    tags:
      - Threat Intelligence
    parameters:
      - in: query
        name: region
        type: string
        description: Filter by region
      - in: query
        name: days
        type: integer
        default: 7
        description: Time range in days
    responses:
      200:
        description: Trending threats ranked by frequency
        schema:
          type: array
          items:
            properties:
              threat_type:
                type: string
              frequency:
                type: integer
              trend_direction:
                type: string
              severity:
                type: string
    """
    days = request.args.get('days', 7, type=int)
    region = request.args.get('region')
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query scans grouped by threat type
    query = db.session.query(
        Threat.type,
        Threat.severity,
        Threat.category,
        func.count(Scan.scan_id).label('frequency')
    ).join(Scan, Scan.threat_id == Threat.threat_id)\
     .filter(Scan.timestamp >= cutoff_date)\
     .group_by(Threat.threat_id)\
     .order_by(func.count(Scan.scan_id).desc())\
     .limit(10)
    
    if region:
        query = query.filter(Scan.location_hint.like(f'%{region}%'))
    
    results = query.all()
    
    trending = []
    for threat_type, severity, category, frequency in results:
        trending.append({
            'threat_type': threat_type,
            'severity': severity,
            'category': category,
            'frequency': frequency,
            'period_days': days,
            'alert_level': 'High' if frequency > 20 else 'Medium' if frequency > 10 else 'Low'
        })
    
    return jsonify({
        'period': f'Last {days} days',
        'region': region or 'All Tunisia',
        'trending_threats': trending
    }), 200
