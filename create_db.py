import os
from src import create_app
from src.models import db, User

def init_db():
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables fresh
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
            print("Database initialized successfully with admin user")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")

if __name__ == '__main__':
    # Delete existing database file if it exists
    db_file = 'aidefense.db'
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Existing database {db_file} removed")
        except Exception as e:
            print(f"Error removing database: {e}")
    
    init_db()
