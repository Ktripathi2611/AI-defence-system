from src import create_app, db
from src.models import User

def check_database():
    app = create_app()
    with app.app_context():
        try:
            users = User.query.all()
            print(f"\nFound {len(users)} users in database:")
            for user in users:
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Role: {user.role}")
                print("-" * 30)
        except Exception as e:
            print(f"Error accessing database: {e}")

if __name__ == '__main__':
    check_database()
