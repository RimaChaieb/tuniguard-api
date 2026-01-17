"""
Unit tests for TuniGuard API
"""
import pytest
from app import create_app, db
from app.models import User, Threat, Scan
from app.utils.helpers import generate_anonymized_id, calculate_risk_score

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def sample_user(app):
    """Create sample user for tests"""
    with app.app_context():
        user = User(
            anonymized_id=generate_anonymized_id(),
            risk_score=50.0,
            scan_count=0
        )
        db.session.add(user)
        db.session.commit()
        return user.user_id

class TestUserManagement:
    """Test user registration and profile endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/api/register', json={})
        assert response.status_code == 201
        data = response.get_json()
        assert 'user_id' in data
        assert 'anonymized_id' in data
        assert data['anonymized_id'].startswith('TG-')
    
    def test_get_user_profile(self, client, sample_user):
        """Test user profile retrieval"""
        response = client.get(f'/api/user/{sample_user}/profile')
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_id'] == sample_user
        assert 'risk_score' in data
        assert 'scan_count' in data
    
    def test_get_nonexistent_user(self, client):
        """Test getting profile for nonexistent user"""
        response = client.get('/api/user/99999/profile')
        assert response.status_code == 404

class TestThreatDetection:
    """Test core scanning functionality"""
    
    def test_health_check(self, client):
        """Test API health endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'online'
    
    def test_scan_validation(self, client, sample_user):
        """Test scan request validation"""
        # Missing required fields
        response = client.post('/api/scan', json={})
        assert response.status_code == 400
        
        # Invalid content_type
        response = client.post('/api/scan', json={
            'user_id': sample_user,
            'content': 'test',
            'content_type': 'invalid'
        })
        assert response.status_code == 400

class TestUtilityFunctions:
    """Test helper functions"""
    
    def test_anonymized_id_generation(self):
        """Test ID generation"""
        id1 = generate_anonymized_id()
        id2 = generate_anonymized_id()
        assert id1 != id2
        assert id1.startswith('TG-')
        assert len(id1) == 9  # TG- + 6 chars
    
    def test_risk_score_calculation(self):
        """Test risk score algorithm"""
        # Empty history
        score = calculate_risk_score([])
        assert score == 50.0
        
        # Mock scan objects
        class MockScan:
            def __init__(self, detection_score):
                self.detection_score = detection_score
        
        # All safe scans
        safe_scans = [MockScan(20) for _ in range(10)]
        score = calculate_risk_score(safe_scans)
        assert score < 50.0
        
        # Mixed scans
        mixed_scans = [MockScan(80) for _ in range(5)] + [MockScan(20) for _ in range(5)]
        score = calculate_risk_score(mixed_scans)
        assert 30 < score < 70

class TestAnalytics:
    """Test analytics endpoints"""
    
    def test_national_analytics(self, client):
        """Test national statistics endpoint"""
        response = client.get('/api/analytics/national')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_scans' in data
        assert 'total_threats_detected' in data
