"""Check scan data in database"""
from app import create_app, db
from app.models import Scan, Threat
from sqlalchemy import func

app = create_app()

with app.app_context():
    # Get all scans
    scans = Scan.query.order_by(Scan.timestamp.desc()).limit(10).all()
    
    print(f"\n📊 Recent Scans (last 10):")
    print("-" * 80)
    for scan in scans:
        print(f"ID: {scan.scan_id} | Score: {scan.detection_score} | Threat ID: {scan.threat_id} | User: {scan.user_id}")
        print(f"Text: {scan.input_text[:60]}...")
        print()
    
    # Get threat detection stats
    print("\n📈 Threat Detection Statistics:")
    print("-" * 80)
    total_scans = Scan.query.count()
    high_score_scans = Scan.query.filter(Scan.detection_score >= 50).count()
    
    print(f"Total scans: {total_scans}")
    print(f"High threat score (>=50): {high_score_scans}")
    
    # Get most common threats
    print("\n🎯 Most Common Threats:")
    print("-" * 80)
    most_common = db.session.query(
        Threat.type,
        func.count(Scan.scan_id).label('count')
    ).join(Scan, Scan.threat_id == Threat.threat_id, isouter=True)\
     .filter(Scan.detection_score >= 50)\
     .group_by(Threat.type)\
     .order_by(func.count(Scan.scan_id).desc())\
     .limit(5)\
     .all()
    
    for threat_type, count in most_common:
        print(f"{threat_type}: {count}")
    
    if not most_common:
        print("No threats detected yet (no scans with score >= 50)")
