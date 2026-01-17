"""
User authentication and registration routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from app.models.schemas import UserSchema
from app.utils.helpers import generate_anonymized_id, log_api_metric
from datetime import datetime
from flasgger import swag_from

bp = Blueprint('auth', __name__, url_prefix='/api')
user_schema = UserSchema()

@bp.route('/register', methods=['POST'])
@log_api_metric('/api/register')
def register():
    """
    Register a new user account with region and carrier selection
    ---
    tags:
      - User Management
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
            - region
            - carrier
          properties:
            username:
              type: string
              description: Unique username
            password:
              type: string
              description: User's password (min 6 chars)
            region:
              type: string
              enum: [Tunis, Sfax, Ariana, Bizerte, Sousse, Monastir, Kairouan, Kasserine, Sidi_Bouzid, Gafsa, Tozeur, Kebili, Tataouine, Ben_Arous, Manouba, Nabeul]
              description: User's region in Tunisia
            carrier:
              type: string
              enum: [Tunisie_Telecom, Orange, Ooredoo, Other]
              description: User's mobile carrier
            city:
              type: string
              description: User's city (optional)
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid request
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists. Please choose another.'}), 400
    
    # Valid regions in Tunisia
    VALID_REGIONS = [
        'Tunis', 'Sfax', 'Ariana', 'Bizerte', 'Sousse', 'Monastir',
        'Kairouan', 'Kasserine', 'Sidi_Bouzid', 'Gafsa', 'Tozeur',
        'Kebili', 'Tataouine', 'Ben_Arous', 'Manouba', 'Nabeul'
    ]
    
    VALID_CARRIERS = ['Tunisie_Telecom', 'Orange', 'Ooredoo', 'Other']
    
    region = data.get('region', 'Tunis')
    carrier = data.get('carrier', 'Other')
    city = data.get('city', 'Unknown')
    
    # Validate region
    if region not in VALID_REGIONS:
        return jsonify({
            'error': 'Invalid region',
            'valid_regions': VALID_REGIONS
        }), 400
    
    # Validate carrier
    if carrier not in VALID_CARRIERS:
        return jsonify({
            'error': 'Invalid carrier',
            'valid_carriers': VALID_CARRIERS
        }), 400
    
    try:
        # Generate unique anonymized ID
        anonymized_id = generate_anonymized_id()
        
        # Create new user
        user = User(
            username=username,
            anonymized_id=anonymized_id,
            region=region,
            city=city,
            carrier=carrier,
            created_at=datetime.utcnow(),
            risk_score=50.0,
            scan_count=0
        )
        
        # Set password (hashed)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'anonymized_id': user.anonymized_id,
            'region': user.region,
            'city': user.city,
            'carrier': user.carrier,
            'message': 'Account created successfully',
            'created_at': user.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
@log_api_metric('/api/login')
def login():
    """
    Login with username and password to get JWT tokens
    ---
    tags:
      - User Management
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: User's username
            password:
              type: string
              description: User's password
    responses:
      200:
        description: Login successful
        schema:
          properties:
            user_id:
              type: integer
            username:
              type: string
            anonymized_id:
              type: string
            access_token:
              type: string
            refresh_token:
              type: string
            message:
              type: string
      401:
        description: Invalid credentials
      404:
        description: User not found
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    try:
        # Create JWT tokens - identity MUST be a string
        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'anonymized_id': user.anonymized_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
@log_api_metric('/api/logout')
def logout():
    """
    Logout user (invalidate current token)
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
        schema:
          properties:
            message:
              type: string
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    return jsonify({
        'message': 'Logout successful',
        'user_id': user_id
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@log_api_metric('/api/refresh')
def refresh():
    """
    Refresh access token using refresh token
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    responses:
      200:
        description: New access token generated
        schema:
          properties:
            access_token:
              type: string
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'access_token': new_access_token,
        'message': 'Token refreshed successfully'
    }), 200

@bp.route('/user/<int:user_id>/profile', methods=['GET'])
@jwt_required()
@log_api_metric('/api/user/profile')
def get_user_profile(user_id):
    """
    Get user security statistics and profile
    ---
    tags:
      - User Management
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User profile retrieved
        schema:
          properties:
            user_id:
              type: integer
            anonymized_id:
              type: string
            created_at:
              type: string
            last_scan:
              type: string
            risk_score:
              type: number
            scan_count:
              type: integer
            security_level:
              type: string
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Determine security level
    if user.risk_score < 30:
        security_level = 'Excellent'
    elif user.risk_score < 50:
        security_level = 'Good'
    elif user.risk_score < 70:
        security_level = 'Fair'
    else:
        security_level = 'At Risk'
    
    return jsonify({
        'user_id': user.user_id,
        'anonymized_id': user.anonymized_id,
        'created_at': user.created_at.isoformat(),
        'last_scan': user.last_scan.isoformat() if user.last_scan else None,
        'risk_score': user.risk_score,
        'scan_count': user.scan_count,
        'security_level': security_level,
        'member_since_days': (datetime.utcnow() - user.created_at).days
    }), 200

@bp.route('/user/<int:user_id>/profile', methods=['PUT'])
@jwt_required()
@log_api_metric('/api/user/update')
def update_user_profile(user_id):
    """
    Update user profile (password)
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            password:
              type: string
              description: New password (min 6 characters)
            old_password:
              type: string
              description: Current password for verification
    responses:
      200:
        description: Profile updated successfully
      400:
        description: Invalid request
      401:
        description: Unauthorized or wrong password
      404:
        description: User not found
    """
    current_user_id = get_jwt_identity()
    
    # Ensure user can only update their own profile
    if str(current_user_id) != str(user_id):
        return jsonify({'error': 'Unauthorized - cannot update other user profiles'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # If changing password, verify old password
    if 'password' in data:
        if not data.get('old_password'):
            return jsonify({'error': 'old_password required to change password'}), 400
        
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Incorrect password'}), 401
        
        if len(data['password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        user.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user_id': user.user_id,
            'username': user.username
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed', 'details': str(e)}), 500

@bp.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
@log_api_metric('/api/user/delete')
def delete_user_account(user_id):
    """
    Delete user account permanently (GDPR compliant)
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - password
          properties:
            password:
              type: string
              description: User's password for verification
    responses:
      200:
        description: Account deleted successfully
      400:
        description: Invalid request
      401:
        description: Unauthorized or wrong password
      404:
        description: User not found
    """
    current_user_id = get_jwt_identity()
    
    # Ensure user can only delete their own account
    if str(current_user_id) != str(user_id):
        return jsonify({'error': 'Unauthorized - cannot delete other accounts'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify password before deletion
    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({'error': 'Password required for account deletion'}), 400
    
    if not user.check_password(data['password']):
        return jsonify({'error': 'Incorrect password'}), 401
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Account deleted successfully',
            'deleted_user': username,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Deletion failed', 'details': str(e)}), 500
