from flask import request, jsonify
from src.usecases.auth_usecase import AuthUseCase
from src.utils.response_template import ResponseTemplate

class AuthController:
    """Controller to handle authentication"""
    
    def __init__(self):
        self.auth_usecase = AuthUseCase()
        self.response = ResponseTemplate()
    
    def login(self):
        """Handler to login"""
        try:
            data = request.get_json()
            
            username = data.get('username') if data else None
            password = data.get('password') if data else None
            
            result = self.auth_usecase.login(username=username, password=password)
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Login successful"
                )
            return self.response.unauthorized(
                message=result.get('error', 'Invalid credentials')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Login failed: {str(e)}"
            )
    
    def register(self):
        """Handler to register new user"""
        try:
            data = request.get_json()
            
            if not data:
                return self.response.bad_request(
                    message='Request body is required'
                )
            
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
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="User registered successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to register user')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Registration failed: {str(e)}"
            )
    
    def get_current_user(self):
        """Handler to get current user info"""
        try:
            # User info dari JWT token (ditambahkan oleh decorator)
            user_id = request.current_user.get('user_id')
            
            result = self.auth_usecase.get_current_user(user_id)
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="User retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', 'User not found')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve user: {str(e)}"
            )
