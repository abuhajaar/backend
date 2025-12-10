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
            # Get current user from JWT token
            current_user = request.current_user
            current_user_id = current_user.get('user_id')
            
            result = self.user_usecase.delete_user(user_id, current_user_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="User deleted successfully"
                )
            return self.response.bad_request(
                message=result.get('error', f'User with ID {user_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete user: {str(e)}"
            )
    
    def get_my_team_users(self):
        """Handler for manager to get users from their department"""
        try:
            # Get current user from JWT token (set by @token_required decorator)
            current_user = request.current_user
            department_id = current_user.get('department_id')
            
            result = self.user_usecase.get_users_by_department(department_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Team users retrieved successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to retrieve team users')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve team users: {str(e)}"
            )
    
    def create_team_user(self):
        """Handler for manager to create user in their department"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            data = request.get_json()
            
            username = data.get('username') if data else None
            email = data.get('email') if data else None
            password = data.get('password') if data else None
            phone = data.get('phone') if data else None
            is_active = data.get('is_active', True) if data else True
            
            # Call manager-specific create method
            result = self.user_usecase.create_user_by_manager(
                username=username,
                email=email,
                password=password,
                phone=phone,
                is_active=is_active,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Employee created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create employee')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create employee: {str(e)}"
            )
    
    def update_team_user(self, user_id):
        """Handler for manager to update user in their department"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            data = request.get_json()
            
            username = data.get('username') if data else None
            email = data.get('email') if data else None
            password = data.get('password') if data else None
            phone = data.get('phone') if data else None
            is_active = data.get('is_active') if data else None
            
            # Call manager-specific update method
            result = self.user_usecase.update_user_by_manager(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                phone=phone,
                is_active=is_active,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Employee updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update employee')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update employee: {str(e)}"
            )
    
    def delete_team_user(self, user_id):
        """Handler for manager to delete user in their department"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_user_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            # Call manager-specific delete method
            result = self.user_usecase.delete_user_by_manager(
                user_id=user_id,
                manager_user_id=manager_user_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.success(
                    data=None,
                    message="Employee deleted successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to delete employee')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete employee: {str(e)}"
            )
