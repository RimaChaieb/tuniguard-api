"""
Database models for TuniGuard
Implements the complete relational structure with all foreign keys
"""
from datetime import datetime
from app import db
from bcrypt import hashpw, gensalt, checkpw

class User(db.Model):
    """User account model with anonymized tracking"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    anonymized_id = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_scan = db.Column(db.DateTime)
    risk_score = db.Column(db.Float, default=0.0)
    scan_count = db.Column(db.Integer, default=0)
    # Region and carrier tracking
    region = db.Column(db.String(100), default='Tunisia')
    city = db.Column(db.String(100), default='Unknown')
    carrier = db.Column(db.String(100), default='Other')
    
    # Relationships
    scans = db.relationship('Scan', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        if not self.password_hash:
            return False
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.anonymized_id}>'


class Threat(db.Model):
    """Catalog of known threat types"""
    __tablename__ = 'threats'
    
    threat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # SMS, Call, App Message
    severity = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical', name='severity_types'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    signature = db.Column(db.Text)  # AI detection pattern
    detection_count = db.Column(db.Integer, default=0)
    
    # Relationships
    scans = db.relationship('Scan', backref='threat', lazy='dynamic')
    intel_reports = db.relationship('ThreatIntel', backref='threat', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Threat {self.type}>'


class Scan(db.Model):
    """Core transaction table - logs every threat analysis"""
    __tablename__ = 'scans'
    
    scan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    threat_id = db.Column(db.Integer, db.ForeignKey('threats.threat_id', ondelete='SET NULL'))
    
    input_text = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=True)  # Add this line
    detection_score = db.Column(db.Float, default=0.0)
    gemini_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    intercept_time = db.Column(db.Float)  # Simulated routing delay in ms
    user_action = db.Column(db.String(50))  # Deleted, Reported, Ignored
    location_hint = db.Column(db.String(100))  # Anonymized region
    
    # Relationships
    conversations = db.relationship('Conversation', backref='scan', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Scan {self.scan_id}>'


class ThreatIntel(db.Model):
    """Aggregates threat trends for predictive analytics"""
    __tablename__ = 'threat_intel'
    
    intel_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    threat_id = db.Column(db.Integer, db.ForeignKey('threats.threat_id'), nullable=False)
    reported_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source_region = db.Column(db.String(100))
    source_country = db.Column(db.String(100), default='Tunisia')
    affected_carriers = db.Column(db.String(500))  # Comma-separated carrier list
    frequency = db.Column(db.Integer, default=1)
    affected_user_count = db.Column(db.Integer, default=1)
    trend_score = db.Column(db.Float, default=0.0)
    escalation_level = db.Column(db.String(50), default='stable')  # stable, monitoring, escalating
    mitigation_status = db.Column(db.String(50), default='open')  # open, mitigated, closed
    ioc_list = db.Column(db.Text)  # Indicators of Compromise
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ThreatIntel {self.intel_id}>'


class Conversation(db.Model):
    """Maintains chatbot dialogue context"""
    __tablename__ = 'conversations'
    
    conv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.scan_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum('user', 'assistant', name='message_roles'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Conversation {self.conv_id}>'


class APIMetric(db.Model):
    """Tracks API performance for optimization"""
    __tablename__ = 'api_metrics'
    
    metric_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    endpoint = db.Column(db.String(100), nullable=False)
    response_time = db.Column(db.Float, nullable=False)  # Milliseconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<APIMetric {self.endpoint}>'
