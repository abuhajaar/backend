from flask import request, jsonify
from src.usecases.user_usecase import UserUseCase
from src.utils.response_template import ResponseTemplate

class UserController:
    """Controller to handle User requests"""
    
    def __init__(self):
        self.user_usecase = UserUseCase()
        self.response = ResponseTemplate()
    
    def get_users(self):
        """Handler to get all users"""
        try:
            result = self.user_usecase.get_all_users()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Users retrieved successfully"
                )
            return self.response.internal_server_error(
                message=result.get('error', 'Failed to retrieve users')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve users: {str(e)}"
            )
    
    def get_user(self, user_id):
        """Handler to get user by ID"""
        try:
            result = self.user_usecase.get_user_by_id(user_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="User retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'User with ID {user_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve user: {str(e)}"
            )
    
    def create_user(self):
        """Handler to create a new user"""
        try:
            data = request.get_json()
            
            username = data.get('username') if data else None
            email = data.get('email') if data else None
            password = data.get('password') if data else None
            phone = data.get('phone') if data else None
            role = data.get('role', 'employee') if data else 'employee'
            department_id = data.get('department_id') if data else None
            status = data.get('status', True) if data else True
            
            result = self.user_usecase.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
                department_id=department_id,
                status=status
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="User created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create user')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create user: {str(e)}"
            )
    
    def update_user(self, user_id):
        """Handler to update user"""
        try:
            data = request.get_json()
            
            username = data.get('username') if data else None
            email = data.get('email') if data else None
            password = data.get('password') if data else None
            phone = data.get('phone') if data else None
            role = data.get('role') if data else None
            department_id = data.get('department_id') if data else None
            status = data.get('status') if data else None
            
            result = self.user_usecase.update_user(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
                department_id=department_id,
                status=status
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="User updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update user')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update user: {str(e)}"
            )
    
    def delete_user(self, user_id):
        """Handler to delete user"""
        try:
            result = self.user_usecase.delete_user(user_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="User deleted successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'User with ID {user_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete user: {str(e)}"
            )
