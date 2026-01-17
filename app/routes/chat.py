"""
Chatbot interaction routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import User, Scan, Conversation
from app.models.schemas import ChatRequestSchema
from app.services.gemini_service import GeminiService
from app.utils.helpers import log_api_metric
from datetime import datetime

bp = Blueprint('chat', __name__, url_prefix='/api')
chat_request_schema = ChatRequestSchema()

@bp.route('/chat', methods=['POST'])
@jwt_required()
@log_api_metric('/api/chat')
def chat_interaction():
    """
    Multi-turn security conversation with AI assistant
    ---
    tags:
      - Chatbot
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - scan_id
            - message
          properties:
            user_id:
              type: integer
              description: User ID
            scan_id:
              type: integer
              description: Related scan ID for context
            message:
              type: string
              description: User's question or message
    responses:
      200:
        description: AI response
        schema:
          properties:
            conv_id:
              type: integer
            response:
              type: string
            timestamp:
              type: string
      400:
        description: Invalid request
      404:
        description: User or scan not found
    """
    # Validate request
    data = request.get_json()
    errors = chat_request_schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    user_id = data['user_id']
    scan_id = data['scan_id']
    user_message = data['message']
    
    # Verify user and scan exist
    user = User.query.get(user_id)
    scan = Scan.query.get(scan_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    if scan.user_id != user_id:
        return jsonify({'error': 'Scan does not belong to user'}), 403
    
    try:
        # Get conversation history
        history = Conversation.query.filter_by(
            scan_id=scan_id,
            user_id=user_id
        ).order_by(Conversation.timestamp.asc()).all()
        
        conversation_history = [
            {'role': conv.role, 'message': conv.message}
            for conv in history
        ]
        
        # Build scan context
        scan_context = {
            'input_text': scan.input_text,
            'threat_detected': scan.detection_score > 50,
            'detection_score': scan.detection_score
        }
        
        # Save user message
        user_conv = Conversation(
            scan_id=scan_id,
            user_id=user_id,
            message=user_message,
            role='user',
            timestamp=datetime.utcnow()
        )
        db.session.add(user_conv)
        
        # Get AI response
        gemini = GeminiService()
        ai_response = gemini.chat_interaction(
            user_message,
            scan_context=scan_context,
            conversation_history=conversation_history
        )
        
        # Save assistant response
        assistant_conv = Conversation(
            scan_id=scan_id,
            user_id=user_id,
            message=ai_response,
            role='assistant',
            timestamp=datetime.utcnow()
        )
        db.session.add(assistant_conv)
        db.session.commit()
        
        return jsonify({
            'conv_id': assistant_conv.conv_id,
            'response': ai_response,
            'timestamp': assistant_conv.timestamp.isoformat(),
            'conversation_length': len(conversation_history) + 2
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Chat failed', 'details': str(e)}), 500

@bp.route('/history/<int:scan_id>', methods=['GET'])
@jwt_required()
@log_api_metric('/api/chat/history')
def get_chat_history(scan_id):
    """
    Retrieve conversation history for a scan
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: path
        name: scan_id
        type: integer
        required: true
        description: Scan ID
      - in: query
        name: user_id
        type: integer
        required: false
        description: User ID (optional)
    responses:
      200:
        description: Chat history retrieved
      404:
        description: Scan not found
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        # Verify scan exists
        scan = Scan.query.get(scan_id)
        if not scan:
            return jsonify({
                'error': 'Scan not found',
                'scan_id': scan_id
            }), 404
        
        # Get chat history for scan
        if user_id:
            conversations = Conversation.query.filter(
                Conversation.scan_id == scan_id,
                Conversation.user_id == user_id
            ).order_by(Conversation.timestamp.asc()).all()
        else:
            conversations = Conversation.query.filter(
                Conversation.scan_id == scan_id
            ).order_by(Conversation.timestamp.asc()).all()
        
        if not conversations:
            return jsonify({
                'scan_id': scan_id,
                'user_id': user_id,
                'message': 'No chat history found',
                'history': []
            }), 200
        
        history = []
        for c in conversations:
            history.append({
                'conv_id': c.conv_id,
                'role': c.role,
                'message': c.message,
                'timestamp': c.timestamp.isoformat()
            })
        
        return jsonify({
            'scan_id': scan_id,
            'user_id': user_id,
            'count': len(history),
            'history': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve history',
            'details': str(e)
        }), 500
