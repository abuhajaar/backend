from typing import Dict
from src.repositories.auth_repository import AuthRepository
from src.utils.jwt_helper import create_access_token
from datetime import timedelta

class AuthUseCase:
    """UseCase untuk authentication"""
    
    def __init__(self):
        self.auth_repository = AuthRepository()
    
    def login(self, username: str, password: str) -> Dict:
        """Login user dengan username dan password"""
        try:
            # Validasi input
            if not username or not password:
                return {
                    'success': False,
                    'error': 'Username and password are required'
                }
            
            # Cari user berdasarkan username
            user = self.auth_repository.get_user_by_username(username)
            
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Check if user is active
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Account is inactive. Please contact administrator.'
                }
            
            # Verify password
            if not user.check_password(password):
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Create JWT token
            token_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'department_id': user.department_id
            }
            
            access_token = create_access_token(token_data)
            
            return {
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'token_type': 'Bearer'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def register(self, username: str, email: str, password: str,
                phone: str = None, role: str = 'user', 
                department_id: int = None) -> Dict:
        """Register user baru"""
        try:
            # Validasi input
            if not username or not email or not password:
                return {
                    'success': False,
                    'error': 'Username, email, and password are required'
                }
            
            # Check if username already exists
            existing_user = self.auth_repository.get_user_by_username(username)
            if existing_user:
                return {
                    'success': False,
                    'error': 'Username already exists'
                }
            
            # Check if email already exists
            existing_email = self.auth_repository.get_user_by_email(email)
            if existing_email:
                return {
                    'success': False,
                    'error': 'Email already exists'
                }
            
            # Create user
            new_user = self.auth_repository.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
                department_id=department_id
            )
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'data': new_user.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_current_user(self, user_id: int) -> Dict:
        """Get current user info"""
        try:
            user = self.auth_repository.get_user_by_id(user_id)
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            return {
                'success': True,
                'data': user.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
