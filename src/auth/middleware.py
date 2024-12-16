from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models import User
from ..utils.monitoring import MonitoringService

monitoring = MonitoringService()

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != 'admin':
                monitoring.logger.warning(f"Unauthorized admin access attempt by user {user_id}")
                return jsonify({'error': 'Admin privileges required'}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def api_key_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key is required'}), 401
                
            if api_key != current_app.config['API_KEY']:
                monitoring.logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
                return jsonify({'error': 'Invalid API key'}), 401
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def rate_limit(requests_per_minute=60):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Get user identity or IP address
            try:
                verify_jwt_in_request()
                identifier = get_jwt_identity()
            except:
                identifier = request.remote_addr
                
            # Check rate limit using Redis
            redis_client = current_app.extensions['redis']
            key = f'rate_limit:{identifier}'
            current = redis_client.get(key)
            
            if current and int(current) >= requests_per_minute:
                monitoring.logger.warning(f"Rate limit exceeded for {identifier}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
                
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)  # Reset after 1 minute
            pipe.execute()
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
