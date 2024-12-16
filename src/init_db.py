from src.models import db
from src.models.user import User
from src.models.scan import Scan
from src.models.deepfake_analysis import DeepFakeAnalysis
from src.models.alert import Alert
from src.models.threat_analysis import ThreatAnalysis
from src.models.notification import Notification
from src import create_app

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create an admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        try:
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
