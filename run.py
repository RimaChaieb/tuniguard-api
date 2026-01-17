"""
TuniGuard Application Entry Point
Run this file to start the Flask server
"""
from flask import render_template
from app import create_app, db
from app.models import Threat
import os
import sys
import traceback

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    try:
        with app.app_context():
            # Create database tables if they don't exist
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Seed threat data if database is empty
            threat_count = Threat.query.count()
            if threat_count == 0:
                print("📋 Seeding threat catalog...")
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
                print(f"✅ Threat catalog seeded with {len(threats)} threats")
            else:
                print(f"✅ Threat catalog already has {threat_count} threats")
        
        print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    TuniGuard API                             ║
    ║        AI-Powered Telecom Security Sentinel for Tunisia      ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Starting TuniGuard API Server...
    
    API Endpoints:
       - Health Check:  http://localhost:5000/api/health
       - Documentation: http://localhost:5000/api/docs
       - Swagger JSON:  http://localhost:5000/api/swagger.json
    
    Don't forget to set your GEMINI_API_KEY in .env file!
    
    📖 Read README.md for full documentation
    
    🇹🇳 Protecting Tunisia's digital communications...
    """)
        
        # Run the application
        print("\nAttempting to start server on port 5000...")
        sys.stdout.flush()
        
        try:
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                use_reloader=False,
                threaded=False
            )
        except Exception as run_error:
            print(f"\nSERVER RUNTIME ERROR: {run_error}")
            traceback.print_exc()
            sys.exit(1)
            
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
