import pytest
from src.models import User

def test_user_registration(client):
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Verify user was created
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.username == 'newuser'

def test_user_login(client, test_user):
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_invalid_login(client):
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

def test_protected_route(client, auth_headers):
    response = client.get('/api/profile', headers=auth_headers)
    assert response.status_code == 200
    assert 'username' in response.json

def test_admin_required(client, auth_headers, admin_user):
    # Regular user access
    response = client.get('/api/admin/users', headers=auth_headers)
    assert response.status_code == 403
    
    # Admin access
    admin_response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'adminpass123'
    })
    admin_headers = {'Authorization': f'Bearer {admin_response.json["access_token"]}'}
    
    response = client.get('/api/admin/users', headers=admin_headers)
    assert response.status_code == 200

def test_password_reset(client, test_user):
    # Request password reset
    response = client.post('/api/auth/reset-password', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 200
    
    # Verify reset token was created
    user = User.query.filter_by(email='test@example.com').first()
    assert user.reset_token is not None
    
    # Reset password
    response = client.post('/api/auth/reset-password/confirm', json={
        'token': user.reset_token,
        'new_password': 'newpassword123'
    })
    assert response.status_code == 200
    
    # Try logging in with new password
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 200
