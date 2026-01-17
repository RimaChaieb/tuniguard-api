"""
Database Initialization Script
Creates tables and populates with Tunisia-specific threat data
"""
from app import create_app, db
from app.models import Threat, User
from app.utils.helpers import generate_anonymized_id
from datetime import datetime

def init_database():
    """Initialize database with schema and seed data"""
    
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate (for clean setup)
        print("🔄 Creating database schema...")
        db.drop_all()
        db.create_all()
        print("✅ Database tables created")
        
        # Seed threat data - Tunisia-specific threats
        print("\n📋 Seeding Tunisia-specific threat catalog...")
        
        threats = [
            {
                'type': 'Fake Telecom Operator',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Fraudulent messages impersonating Tunisie Telecom, Ooredoo, or Orange Tunisia to harvest personal data or payment information',
                'signature': 'Contains operator brand names with suspicious links or payment requests'
            },
            {
                'type': 'Mobile Money Phishing',
                'category': 'SMS',
                'severity': 'Critical',
                'description': 'Scams targeting D17, Flouci, or Sobflous mobile payment users with fake transaction alerts',
                'signature': 'References mobile payment services with urgent account verification requests'
            },
            {
                'type': 'Banking Impersonation',
                'category': 'SMS',
                'severity': 'Critical',
                'description': 'Phishing attempts mimicking Tunisian banks (Zitouna, Attijari, BIAT, BNA) requesting credentials',
                'signature': 'Bank name + urgent account issue + credential request or suspicious link'
            },
            {
                'type': 'Premium Rate Scam',
                'category': 'Call',
                'severity': 'Medium',
                'description': 'Calls that encourage callback to premium-rate numbers, resulting in high charges',
                'signature': 'Missed call from unknown number with international prefix or premium rate pattern'
            },
            {
                'type': 'Fake Prize Offer',
                'category': 'SMS',
                'severity': 'Medium',
                'description': 'Claims user won telecom credit, prizes, or lottery requiring personal data or payment',
                'signature': 'Congratulations + prize/money won + request for CIN or payment to claim'
            },
            {
                'type': 'SIM Swap Social Engineering',
                'category': 'Call',
                'severity': 'High',
                'description': 'Fraudsters posing as telecom support to gather info for SIM swap attacks',
                'signature': 'Call requesting CIN, personal details, or verification codes from "operator"'
            },
            {
                'type': 'Fake E-commerce Deal',
                'category': 'App Message',
                'severity': 'Medium',
                'description': 'Too-good-to-be-true product offers requiring advance payment via mobile money',
                'signature': 'Unrealistic prices + D17/Flouci payment to personal number + urgency'
            },
            {
                'type': 'Government Subsidy Fraud',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Exploits government aid programs, requesting personal data to "claim" benefits',
                'signature': 'References Tunisian subsidies/aid programs with data submission requests'
            },
            {
                'type': 'Currency Exchange Scam',
                'category': 'App Message',
                'severity': 'Medium',
                'description': 'Illegal currency exchange offers at favorable rates, results in theft or counterfeit',
                'signature': 'EUR/USD exchange at rates better than official + meet-up or advance payment'
            },
            {
                'type': 'Delivery Impersonation',
                'category': 'SMS',
                'severity': 'Low',
                'description': 'Fake delivery notifications from Aramex, La Poste Tunisienne, or e-commerce sites',
                'signature': 'Delivery notification + suspicious link + payment/personal data request'
            },
            {
                'type': 'Tech Support Scam',
                'category': 'Call',
                'severity': 'Medium',
                'description': 'Fake technical support claiming device infection, requesting remote access',
                'signature': 'Unsolicited call about device problems + remote access request'
            },
            {
                'type': 'Romantic Scam',
                'category': 'App Message',
                'severity': 'Low',
                'description': 'Fake romantic interest leading to financial exploitation',
                'signature': 'Quick emotional attachment + eventual money request for "emergency"'
            },
            {
                'type': 'Investment Fraud',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Fake investment opportunities in crypto, forex, or business schemes',
                'signature': 'Guaranteed high returns + pressure to invest quickly + WhatsApp/Telegram contact'
            },
            {
                'type': 'Fake Job Offer',
                'category': 'App Message',
                'severity': 'Low',
                'description': 'Fraudulent employment offers requiring upfront fees or personal documents',
                'signature': 'Remote job + high salary + request for CIN copy or registration fee'
            },
            {
                'type': 'Charity Scam',
                'category': 'SMS',
                'severity': 'Low',
                'description': 'Fake charitable organizations exploiting religious or humanitarian causes',
                'signature': 'Emotional appeal + donation request to personal account + no official org info'
            }
        ]
        
        for threat_data in threats:
            threat = Threat(**threat_data)
            db.session.add(threat)
        
        db.session.commit()
        print(f"✅ Added {len(threats)} threat types to catalog")
        
        # Create demo user
        print("\n👤 Creating demo user...")
        demo_user = User(
            username='demo_user',
            anonymized_id=generate_anonymized_id(),
            created_at=datetime.utcnow(),
            risk_score=50.0,
            scan_count=0
        )
        demo_user.set_password('demo123')  # Set a default password
        db.session.add(demo_user)
        db.session.commit()
        
        print(f"✅ Demo user created: {demo_user.anonymized_id} (ID: {demo_user.user_id})")
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║              ✅ Database Initialization Complete!             ║
╚══════════════════════════════════════════════════════════════╝

📊 Database Summary:
   - Tables Created: 6 (users, threats, scans, threat_intel, conversations, api_metrics)
   - Threats Loaded: 15 Tunisia-specific threat types
   - Demo User: Ready for testing

🚀 Next Steps:
   1. Copy .env.example to .env
   2. Add your GEMINI_API_KEY to .env
   3. Run: python run.py
   4. Visit: http://localhost:5000/api/docs

📖 Full documentation in README.md
        """)

if __name__ == '__main__':
    init_database()
