"""
Core threat scanning routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app import db
from app.models import User, Threat, Scan, ThreatIntel
from app.models.schemas import ScanRequestSchema, ScanResponseSchema
from app.services.gemini_service import GeminiService
from app.utils.helpers import (
    simulate_intercept_time, 
    calculate_risk_score, 
    log_api_metric,
    sanitize_input,
    get_threat_signal_bars
)
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('scans', __name__, url_prefix='/api')
scan_request_schema = ScanRequestSchema()
scan_response_schema = ScanResponseSchema()

@bp.route('/scan', methods=['POST'])
@jwt_required()
@log_api_metric('/api/scan')
def analyze_threat():
    """
    Analyze suspicious content for threats using AI
    ---
    tags:
      - Threat Detection
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - content
            - content_type
          properties:
            user_id:
              type: integer
              description: User ID
            content:
              type: string
              description: Suspicious message/call content
            content_type:
              type: string
              enum: [sms, call, app_message]
              description: Type of content
            location_hint:
              type: string
              description: Optional location (e.g., "Tunis")
    responses:
      200:
        description: Threat analysis completed
        schema:
          properties:
            scan_id:
              type: integer
            threat_detected:
              type: boolean
            detection_score:
              type: number
            threat_type:
              type: string
            severity:
              type: string
            advice:
              type: string
            signal_bars:
              type: string
            intercept_time:
              type: number
            timestamp:
              type: string
      400:
        description: Invalid request
      404:
        description: User not found
    """
    # Validate request
    data = request.get_json()
    errors = scan_request_schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    user_id = data['user_id']
    content = sanitize_input(data['content'])
    content_type = data['content_type']
    location_hint = data.get('location_hint', '')
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Simulate telecom intercept delay
        intercept_time = simulate_intercept_time()
        
        # Analyze with Gemini AI
        gemini = GeminiService()
        ai_result = gemini.analyze_threat(content, content_type)
        
        # Find or create threat type
        threat = None
        if ai_result['threat_detected']:
            threat_type = ai_result['threat_type']
            
            # First try exact match
            threat = Threat.query.filter_by(type=threat_type).first()
            
            # If not found, try fuzzy matching with keywords
            if not threat:
                threat_keywords = {
                    'Phishing': ['Phishing', 'Smishing', 'Email'],
                    'Payment': ['Payment', 'Money', 'Transfer'],
                    'Banking': ['Bank', 'Account', 'Finance'],
                    'Government': ['Government', 'Authority', 'Official'],
                    'Tech': ['Tech', 'Support', 'Microsoft', 'Apple'],
                    'Investment': ['Investment', 'Stock', 'Crypto'],
                    'Scam': ['Scam', 'Fraud'],
                    'Malware': ['Malware', 'Virus', 'Trojan']
                }
                
                for keyword_type, keywords in threat_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in threat_type.lower():
                            # Find threat containing this keyword
                            threat = Threat.query.filter(
                                Threat.type.ilike(f'%{keyword}%')
                            ).first()
                            if threat:
                                break
                    if threat:
                        break
            
            # If still not found, default to first threat
            if not threat:
                threat = Threat.query.first()
            
            if threat:
                threat.detection_count += 1
        
        # Create scan record
        scan = Scan(
            user_id=user_id,
            threat_id=threat.threat_id if threat else None,
            input_text=content,
            content_type=content_type,
            detection_score=ai_result['score'],
            gemini_response=str(ai_result),
            timestamp=datetime.utcnow(),
            intercept_time=intercept_time,
            location_hint=f"{user.city}, {user.region}" if user.city else user.region
        )
        
        db.session.add(scan)
        db.session.flush()  # Get scan_id before commit
        
        # ✅ AUTO-UPDATE THREATINTEL with region and carrier
        if threat and ai_result['threat_detected'] and ai_result['score'] > 0.5:
            from datetime import date
            
            today = date.today()
            
            # Check if ThreatIntel record exists for this threat + region + today
            intel = ThreatIntel.query.filter(
                ThreatIntel.threat_id == threat.threat_id,
                ThreatIntel.source_region == user.region,
                func.date(ThreatIntel.reported_date) == today
            ).first()
            
            if intel:
                # Update existing record
                intel.frequency += 1
                intel.affected_user_count += 1
                
                # Update carrier info
                if intel.affected_carriers:
                    carriers = set(intel.affected_carriers.split(','))
                    carriers.add(user.carrier)
                    intel.affected_carriers = ','.join(carriers)
                else:
                    intel.affected_carriers = user.carrier
                
                # Determine escalation level based on frequency
                if intel.frequency >= 10:
                    intel.escalation_level = 'escalating'
                    intel.trend_score = min(100, intel.trend_score + 5)
                elif intel.frequency >= 5:
                    intel.escalation_level = 'monitoring'
                    intel.trend_score = min(100, intel.trend_score + 2)
                else:
                    intel.escalation_level = 'stable'
                
                intel.updated_at = datetime.utcnow()
            else:
                # Create new ThreatIntel record
                intel = ThreatIntel(
                    threat_id=threat.threat_id,
                    reported_date=datetime.utcnow(),
                    source_region=user.region,
                    source_country='Tunisia',
                    affected_carriers=user.carrier,
                    frequency=1,
                    trend_score=50.0,
                    escalation_level='stable',
                    affected_user_count=1,
                    mitigation_status='open',
                    ioc_list=content[:100],
                    created_at=datetime.utcnow()
                )
                db.session.add(intel)
        
        # Update user statistics
        user.scan_count += 1
        user.last_scan = datetime.utcnow()
        
        # Recalculate risk score
        recent_scans = Scan.query.filter_by(user_id=user_id)\
            .order_by(Scan.timestamp.desc())\
            .limit(20)\
            .all()
        user.risk_score = calculate_risk_score(recent_scans)
        
        db.session.commit()
        
        # Build comprehensive response
        advice_parts = [ai_result['explanation']]
        if ai_result.get('safe_actions'):
            advice_parts.append('Actions: ' + ', '.join(ai_result['safe_actions'][:3]))
        
        response = {
            'scan_id': scan.scan_id,
            'threat_detected': ai_result['threat_detected'],
            'detection_score': ai_result['score'],
            'threat_type': ai_result['threat_type'],
            'severity': ai_result['severity'],
            'advice': ' | '.join(advice_parts),
            'explanation': ai_result['explanation'],
            'red_flags': ai_result.get('red_flags', []),
            'safe_actions': ai_result.get('safe_actions', []),
            'signal_bars': get_threat_signal_bars(ai_result['score']),
            'intercept_time': intercept_time,
            'timestamp': scan.timestamp.isoformat(),
            'cultural_context': ai_result.get('cultural_context', ''),
            'user_risk_score': user.risk_score
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Scan error: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@bp.route('/scan/batch', methods=['POST'])
@jwt_required()
@log_api_metric('/api/scan/batch')
def batch_scan():
    """
    Scan multiple messages simultaneously
    ---
    tags:
      - Threat Detection
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
            scans:
              type: array
              items:
                type: object
                properties:
                  content:
                    type: string
                  content_type:
                    type: string
    responses:
      200:
        description: Batch scan completed
        schema:
          type: object
          properties:
            total_scanned:
              type: integer
            threats_found:
              type: integer
            results:
              type: array
    """
    data = request.get_json()
    user_id = data.get('user_id')
    scans_data = data.get('scans', [])
    
    if not user_id or not scans_data:
        return jsonify({'error': 'user_id and scans array required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    results = []
    threats_found = 0
    
    try:
        gemini = GeminiService()
        
        for scan_data in scans_data[:50]:  # Limit to 50 per batch
            content = sanitize_input(scan_data.get('content', ''))
            content_type = scan_data.get('content_type', 'sms')
            
            ai_result = gemini.analyze_threat(content, content_type)
            
            if ai_result['threat_detected']:
                threats_found += 1
            
            results.append({
                'content_preview': content[:50] + '...' if len(content) > 50 else content,
                'threat_detected': ai_result['threat_detected'],
                'score': ai_result['score'],
                'threat_type': ai_result['threat_type']
            })
        
        return jsonify({
            'total_scanned': len(results),
            'threats_found': threats_found,
            'safe_messages': len(results) - threats_found,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Batch scan failed', 'details': str(e)}), 500

@bp.route('/scan/<int:scan_id>', methods=['GET'])
@jwt_required()
@log_api_metric('/api/scan/detail')
def get_scan_detail(scan_id):
    """
    Get detailed information about a specific scan
    ---
    tags:
      - Threat Detection
    parameters:
      - in: path
        name: scan_id
        type: integer
        required: true
    responses:
      200:
        description: Scan details
      404:
        description: Scan not found
    """
    scan = Scan.query.get(scan_id)
    
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({
        'scan_id': scan.scan_id,
        'user_id': scan.user_id,
        'input_text': scan.input_text,
        'detection_score': scan.detection_score,
        'threat_type': scan.threat.type if scan.threat else 'Safe',
        'timestamp': scan.timestamp.isoformat(),
        'intercept_time': scan.intercept_time,
        'user_action': scan.user_action,
        'location_hint': scan.location_hint
    }), 200
