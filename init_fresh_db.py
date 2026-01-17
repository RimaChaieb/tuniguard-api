from app import create_app, db

app = create_app()
with app.app_context():
    # Drop all tables first
    db.drop_all()
    # Create all tables fresh
    db.create_all()
    print("✓ Database recreated successfully with all tables!")
