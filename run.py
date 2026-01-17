"""
TuniGuard Application Entry Point
Run this file to start the Flask server
"""
from flask import render_template
from app import create_app, db
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
                host='127.0.0.1',
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
