import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        'exp': expire,
        'iat': datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to validate JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format. Use: Bearer <token>',
                    'status_code': 401
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing',
                'status_code': 401
            }), 401
        
        # Decode token
        payload = decode_access_token(token)
        
        if payload is None:
            return jsonify({
                'success': False,
                'message': 'Token is invalid or expired',
                'status_code': 401
            }), 401
        
        # Pass user info to route
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(allowed_roles: list):
    """Decorator to validate user role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Check if user has valid token first
            if not hasattr(request, 'current_user'):
                return jsonify({
                    'success': False,
                    'message': 'Authentication required',
                    'status_code': 401
                }), 401
            
            user_role = request.current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': 'Access forbidden. Insufficient permissions.',
                    'status_code': 403
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator
