from src import create_app, db
from src.models import User
from datetime import datetime

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            name='Administrator',
            role='Admin',
            is_active=True
        )
        admin.set_password('admin123')
        
        # Add to database
        db.session.add(admin)
        try:
            db.session.commit()
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_user()
