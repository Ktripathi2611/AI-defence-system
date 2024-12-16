import pytest
from src import create_app, db
from src.models import User, Scan, Notification
from datetime import datetime

@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def test_scan(app, test_user):
    with app.app_context():
        scan = Scan(
            filename='test.pdf',
            file_path='/tmp/test.pdf',
            file_type='application/pdf',
            status='completed',
            threat_level=50,
            user_id=test_user.id,
            timestamp=datetime.utcnow(),
            results={
                'threats_found': [
                    {'type': 'malware', 'severity': 'high'}
                ]
            }
        )
        db.session.add(scan)
        db.session.commit()
        return scan

@pytest.fixture
def test_notification(app, test_user):
    with app.app_context():
        notification = Notification(
            user_id=test_user.id,
            type='threat_alert',
            data={'message': 'Test notification'},
            read=False
        )
        db.session.add(notification)
        db.session.commit()
        return notification
