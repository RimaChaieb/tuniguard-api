"""
Marshmallow schemas for request/response validation
"""
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """User serialization schema"""
    user_id = fields.Int(dump_only=True)
    anonymized_id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_scan = fields.DateTime(dump_only=True)
    risk_score = fields.Float(dump_only=True)
    scan_count = fields.Int(dump_only=True)

class ThreatSchema(Schema):
    """Threat serialization schema"""
    threat_id = fields.Int(dump_only=True)
    type = fields.Str(required=True)
    category = fields.Str(required=True, validate=validate.OneOf(['SMS', 'Call', 'App Message']))
    severity = fields.Str(required=True, validate=validate.OneOf(['Low', 'Medium', 'High', 'Critical']))
    description = fields.Str(required=True)
    signature = fields.Str(allow_none=True)
    detection_count = fields.Int(dump_only=True)

class ScanRequestSchema(Schema):
    """Scan request validation schema"""
    user_id = fields.Int(required=True)
    content = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    content_type = fields.Str(required=True, validate=validate.OneOf(['sms', 'call', 'app_message']))
    location_hint = fields.Str(required=False, allow_none=True)

class ScanResponseSchema(Schema):
    """Scan response schema"""
    scan_id = fields.Int()
    threat_detected = fields.Bool()
    detection_score = fields.Float()
    threat_type = fields.Str(allow_none=True)
    severity = fields.Str(allow_none=True)
    advice = fields.Str()
    intercept_time = fields.Float()
    timestamp = fields.DateTime()

class ChatRequestSchema(Schema):
    """Chat request validation schema"""
    user_id = fields.Int(required=True)
    scan_id = fields.Int(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))

class ChatResponseSchema(Schema):
    """Chat response schema"""
    conv_id = fields.Int()
    response = fields.Str()
    timestamp = fields.DateTime()
