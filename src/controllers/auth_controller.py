from flask import request, jsonify
from src.usecases.auth_usecase import AuthUseCase

class AuthController:
    """Controller untuk authentication"""
    
    def __init__(self):
        self.auth_usecase = AuthUseCase()
    
    def login(self):
        """Handler untuk login"""
        print("AuthController: login called")
        data = request.get_json()
        
        username = data.get('username') if data else None
        password = data.get('password') if data else None
        
        result = self.auth_usecase.login(username=username, password=password)
        status_code = 200 if result['success'] else 401
        
        return jsonify(result), status_code
    
    def register(self):
        """Handler untuk register user baru"""
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        role = data.get('role', 'user')
        department_id = data.get('department_id')
        
        result = self.auth_usecase.register(
            username=username,
            email=email,
            password=password,
            phone=phone,
            role=role,
            department_id=department_id
        )
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    def get_current_user(self):
        """Handler untuk get current user info"""
        # User info dari JWT token (ditambahkan oleh decorator)
        user_id = request.current_user.get('user_id')
        
        result = self.auth_usecase.get_current_user(user_id)
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
