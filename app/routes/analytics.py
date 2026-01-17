"""
Analytics Routes
Provides endpoints for analytics and reporting
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Scan, Threat
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for analytics service"""
    return jsonify({'status': 'healthy', 'service': 'analytics'}), 200

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get current user's threat statistics"""
    user_id = get_jwt_identity()
    days = request.args.get('days', default=30, type=int)
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query user's scans
    scans = Scan.query.filter(
        Scan.user_id == user_id,
        Scan.timestamp >= start_date
    ).all()
    
    # Calculate statistics
    total_scans = len(scans)
    threats_detected = sum(1 for scan in scans if scan.detection_score > 50)
    avg_score = sum(scan.detection_score for scan in scans) / total_scans if total_scans > 0 else 0
    
    # Group by content type
    content_types = {}
    for scan in scans:
        ct = scan.content_type or 'unknown'
        if ct not in content_types:
            content_types[ct] = {'total': 0, 'threats': 0}
        content_types[ct]['total'] += 1
        if scan.detection_score > 50:
            content_types[ct]['threats'] += 1
    
    return jsonify({
        'user_id': user_id,
        'period_days': days,
        'total_scans': total_scans,
        'threats_detected': threats_detected,
        'average_threat_score': round(avg_score, 2),
        'threat_percentage': round((threats_detected / total_scans * 100) if total_scans > 0 else 0, 2),
        'by_content_type': content_types
    }), 200

@bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def user_analytics(user_id):
    """Get user-specific analytics"""
    days = request.args.get('days', default=30, type=int)
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query user's scans
    scans = Scan.query.filter(
        Scan.user_id == user_id,
        Scan.timestamp >= start_date  # Updated attribute
    ).all()
    
    # Calculate statistics
    total_scans = len(scans)
    threats_detected = sum(1 for scan in scans if scan.detection_score > 50)
    avg_score = sum(scan.detection_score for scan in scans) / total_scans if total_scans > 0 else 0
    
    return jsonify({
        'user_id': user_id,
        'period_days': days,
        'total_scans': total_scans,
        'threats_detected': threats_detected,
        'average_threat_score': round(avg_score, 2),
        'threat_percentage': round((threats_detected / total_scans * 100) if total_scans > 0 else 0, 2)
    }), 200

@bp.route('/national', methods=['GET'])
def national_analytics():
    """Get national-level analytics"""
    days = request.args.get('days', default=7, type=int)
    
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query all scans with threat info
    scans = Scan.query.filter(Scan.timestamp >= start_date).all()
    
    # Calculate statistics
    total_scans = len(scans)
    threats_detected = sum(1 for scan in scans if scan.detection_score > 50)
    avg_score = sum(scan.detection_score for scan in scans) / total_scans if total_scans > 0 else 0
    
    # Group by content type
    content_types = {}
    for scan in scans:
        ct = scan.content_type or 'unknown'
        if ct not in content_types:
            content_types[ct] = {'total': 0, 'threats': 0}
        content_types[ct]['total'] += 1
        if scan.detection_score > 50:
            content_types[ct]['threats'] += 1
    
    # Get most common threats (by threat type)
    threat_counts = db.session.query(
        Threat.type,
        func.count(Scan.scan_id).label('count')
    ).join(Threat, Scan.threat_id == Threat.threat_id).filter(
        Scan.timestamp >= start_date,
        Scan.threat_id.isnot(None)
    ).group_by(Threat.type).order_by(
        func.count(Scan.scan_id).desc()
    ).limit(5).all()
    
    most_common_threats = [
        {'threat_type': threat[0], 'count': threat[1]}
        for threat in threat_counts
    ] if threat_counts else []
    
    return jsonify({
        'period_days': days,
        'total_scans': total_scans,
        'threats_detected': threats_detected,
        'average_threat_score': round(avg_score, 2),
        'threat_percentage': round((threats_detected / total_scans * 100) if total_scans > 0 else 0, 2),
        'by_content_type': content_types,
        'most_common_threats': most_common_threats
    }), 200

@bp.route('/performance', methods=['GET'])
def performance_metrics():
    """Get performance metrics"""
    hours = request.args.get('hours', default=24, type=int)
    
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    # Query recent scans
    scans = Scan.query.filter(Scan.timestamp >= start_date).all()  # Updated attribute
    
    # Calculate performance metrics
    total_scans = len(scans)
    avg_processing_time = 0.5  # Placeholder - implement actual timing if needed
    uptime_percentage = 99.9  # Placeholder
    
    return jsonify({
        'period_hours': hours,
        'total_scans': total_scans,
        'average_processing_time_seconds': avg_processing_time,
        'uptime_percentage': uptime_percentage,
        'scans_per_hour': round(total_scans / hours, 2) if hours > 0 else 0
    }), 200