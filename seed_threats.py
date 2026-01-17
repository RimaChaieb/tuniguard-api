"""
Seed the database with initial threat data
"""
from app import create_app, db
from app.models import Threat

def seed_threats():
    """Add initial threat types to the database"""
    app = create_app()
    
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Check if threats already exist
        existing_count = Threat.query.count()
        if existing_count > 0:
            print(f"✅ Database already has {existing_count} threats")
            return
        
        threats = [
            {
                'type': 'SMS Phishing (Smishing)',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Fraudulent SMS messages pretending to be from legitimate organizations to steal personal information',
                'signature': 'urgent action, click link, verify account, suspicious URLs'
            },
            {
                'type': 'Payment Scam',
                'category': 'SMS',
                'severity': 'Critical',
                'description': 'Fake payment requests or lottery winnings designed to extract money',
                'signature': 'won prize, transfer money, urgent payment, bank details'
            },
            {
                'type': 'Fake Mobile Money',
                'category': 'SMS',
                'severity': 'Critical',
                'description': 'Impersonation of mobile money services (Ooredoo, Orange Money, etc.)',
                'signature': 'Ooredoo, Orange Money, mobile money, transfer failed, account blocked'
            },
            {
                'type': 'Bank Impersonation',
                'category': 'SMS',
                'severity': 'Critical',
                'description': 'Messages pretending to be from banks requesting sensitive information',
                'signature': 'bank, ATM, card blocked, verify identity, suspicious activity'
            },
            {
                'type': 'Government Impersonation',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Fake messages claiming to be from government agencies',
                'signature': 'government, ministry, fine, tax, official notice'
            },
            {
                'type': 'Tech Support Scam',
                'category': 'Call',
                'severity': 'Medium',
                'description': 'Fake technical support calls claiming device issues',
                'signature': 'computer virus, technical support, remote access, software issue'
            },
            {
                'type': 'Romance Scam',
                'category': 'App Message',
                'severity': 'High',
                'description': 'Fraudulent romantic relationships to extract money',
                'signature': 'love, relationship, emergency funds, travel money, meet in person'
            },
            {
                'type': 'Job Offer Scam',
                'category': 'SMS',
                'severity': 'Medium',
                'description': 'Fake job opportunities requiring upfront payment',
                'signature': 'job offer, work from home, easy money, registration fee'
            },
            {
                'type': 'Delivery Notification Scam',
                'category': 'SMS',
                'severity': 'Medium',
                'description': 'Fake delivery or package notifications with malicious links',
                'signature': 'package, delivery, shipment, track order, customs fee'
            },
            {
                'type': 'COVID-19 Related Scam',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Exploitation of pandemic-related concerns',
                'signature': 'vaccine, COVID, pandemic, health pass, test result'
            },
            {
                'type': 'Charity Scam',
                'category': 'SMS',
                'severity': 'Medium',
                'description': 'Fake charitable organizations requesting donations',
                'signature': 'donation, charity, help, humanitarian, disaster relief'
            },
            {
                'type': 'Investment Scam',
                'category': 'App Message',
                'severity': 'Critical',
                'description': 'Fraudulent investment opportunities promising high returns',
                'signature': 'investment, crypto, bitcoin, guaranteed returns, passive income'
            },
            {
                'type': 'Identity Theft',
                'category': 'SMS',
                'severity': 'Critical',
                'description': 'Attempts to steal personal identification information',
                'signature': 'verify identity, social security, ID number, passport, birth certificate'
            },
            {
                'type': 'Account Takeover',
                'category': 'SMS',
                'severity': 'High',
                'description': 'Unauthorized access attempts to online accounts',
                'signature': 'password reset, suspicious login, account access, verification code'
            },
            {
                'type': 'Malware Distribution',
                'category': 'App Message',
                'severity': 'Critical',
                'description': 'Messages containing malicious links or attachments',
                'signature': 'download app, install software, click here, open attachment'
            }
        ]
        
        print(f"📝 Adding {len(threats)} threat types to database...")
        
        for threat_data in threats:
            threat = Threat(
                type=threat_data['type'],
                category=threat_data['category'],
                severity=threat_data['severity'],
                description=threat_data['description'],
                signature=threat_data['signature'],
                detection_count=0
            )
            db.session.add(threat)
        
        db.session.commit()
        print(f"✅ Successfully added {len(threats)} threat types!")
        
        # Display summary
        print("\n📊 Threat Catalog Summary:")
        print(f"  - Critical: {sum(1 for t in threats if t['severity'] == 'Critical')}")
        print(f"  - High: {sum(1 for t in threats if t['severity'] == 'High')}")
        print(f"  - Medium: {sum(1 for t in threats if t['severity'] == 'Medium')}")
        print(f"  - SMS: {sum(1 for t in threats if t['category'] == 'SMS')}")
        print(f"  - Call: {sum(1 for t in threats if t['category'] == 'Call')}")
        print(f"  - App Message: {sum(1 for t in threats if t['category'] == 'App Message')}")

if __name__ == '__main__':
    seed_threats()
