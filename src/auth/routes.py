from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, User
from ..utils.monitoring import MonitoringService

auth = Blueprint('auth', __name__)
monitoring = MonitoringService()

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
        
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        monitoring.logger.info(f"New user registered: {user.username}")
        return jsonify({'message': 'User registered successfully'})
    except Exception as e:
        monitoring.logger.error(f"Registration failed: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        monitoring.logger.info(f"User logged in: {user.username}")
        return jsonify({'message': 'Logged in successfully', 'user': user.to_dict()})
        
    monitoring.logger.warning(f"Failed login attempt for email: {data['email']}")
    return jsonify({'error': 'Invalid credentials'}), 401

@auth.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    monitoring.logger.info(f"User logged out: {username}")
    return jsonify({'message': 'Logged out successfully'})

@auth.route('/profile')
@login_required
def get_profile():
    return jsonify(current_user.to_dict())
