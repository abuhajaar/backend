from typing import List, Dict, Optional
from src.repositories.user_repository import UserRepository
from src.repositories.booking_repository import BookingRepository
from src.repositories.department_repository import DepartmentRepository
from src.config.database import db

class UserUseCase:
    """UseCase for business logic User"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.booking_repository = BookingRepository()
        self.department_repository = DepartmentRepository()
    
    def get_all_users(self) -> Dict:
        """Get all users with total bookings"""
        try:
            users = self.user_repository.get_all()
            users_list = []
            
            for user in users:
                user_data = user.to_dict()
                
                # Count total bookings for this user via repository
                total_bookings = self.booking_repository.count_by_user_id(user.id)
                user_data['total_bookings'] = total_bookings
                
                # Get department name
                if user.department_id:
                    department = self.department_repository.get_by_id(user.department_id)
                    user_data['department_name'] = department.name if department else None
                else:
                    user_data['department_name'] = None
                
                users_list.append(user_data)
            
            return {
                'success': True,
                'data': users_list,
                'count': len(users_list)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_by_id(self, user_id: int) -> Dict:
        """Get user by ID"""
        try:
            user = self.user_repository.get_by_id(user_id)
            if user:
                return {
                    'success': True,
                    'data': user.to_dict()
                }
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_users_by_department(self, department_id: int) -> Dict:
        """Get all users from a specific department (for manager)"""
        try:
            if not department_id:
                return {
                    'success': False,
                    'error': 'Department ID is required'
                }
            
            # Get department info
            department = self.department_repository.get_by_id(department_id)
            if not department:
                return {
                    'success': False,
                    'error': 'Department not found'
                }
            
            # Get all users from this department
            users = self.user_repository.get_by_department_id(department_id)
            users_list = []
            
            for user in users:
                user_data = user.to_dict()
                
                # Count total bookings for this user
                total_bookings = self.booking_repository.count_by_user_id(user.id)
                user_data['total_bookings'] = total_bookings
                
                users_list.append(user_data)
            
            return {
                'success': True,
                'data': {
                    'department': department.to_dict(),
                    'users': users_list,
                    'total_users': len(users_list)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_user(self, username: str, email: str, password: str, 
                    phone: str = None, role: str = 'employee', 
                    department_id: int = None, status: bool = True) -> Dict:
        """Create a new user"""
        try:
            # Validasi input
            if not username or not email or not password:
                return {
                    'success': False,
                    'error': 'Username, email, and password are required'
                }
            
            # Validate role
            valid_roles = ['employee', 'manager', 'superadmin']
            if role not in valid_roles:
                return {
                    'success': False,
                    'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
                }
            
            # Cek apakah username sudah ada
            existing_username = self.user_repository.get_by_username(username)
            if existing_username:
                return {
                    'success': False,
                    'error': 'Username already exists'
                }
            
            # Cek apakah email sudah ada
            existing_user = self.user_repository.get_by_email(email)
            if existing_user:
                return {
                    'success': False,
                    'error': 'Email already exists'
                }
            
            # Validate department if provided
            if department_id:
                department = self.department_repository.get_by_id(department_id)
                if not department:
                    return {
                        'success': False,
                        'error': 'Department not found'
                    }
                
                # Check if trying to assign manager role to department that already has a manager
                if role == 'manager' and department.manager_id is not None:
                    existing_manager = self.user_repository.get_by_id(department.manager_id)
                    if existing_manager:
                        return {
                            'success': False,
                            'error': f'Department already has a manager: {existing_manager.username}. Only one manager per department is allowed.'
                        }
            
            # Buat user baru
            new_user = self.user_repository.create(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
                department_id=department_id,
                is_active=status
            )
            
            # Auto-assign manager_id to department if user role is 'manager' and has department
            if new_user.role == 'manager' and new_user.department_id:
                department = self.department_repository.get_by_id(new_user.department_id)
                if department and department.manager_id is None:
                    # Update department's manager_id if not already assigned
                    self.department_repository.update_manager(new_user.department_id, new_user.id)
            
            user_data = new_user.to_dict()
            
            # Add department name
            if new_user.department_id:
                department = self.department_repository.get_by_id(new_user.department_id)
                user_data['department_name'] = department.name if department else None
            else:
                user_data['department_name'] = None
            
            return {
                'success': True,
                'data': user_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_user(self, user_id: int, username: str = None, email: str = None, 
                    password: str = None, phone: str = None, role: str = None, 
                    department_id: int = None, status: bool = None) -> Dict:
        """Update user"""
        try:
            # Check if user exists
            existing = self.user_repository.get_by_id(user_id)
            if not existing:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Validate role if provided
            if role is not None:
                valid_roles = ['employee', 'manager', 'superadmin']
                if role not in valid_roles:
                    return {
                        'success': False,
                        'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
                    }
            
            # Cek apakah username baru sudah digunakan user lain
            if username is not None:
                existing_username = self.user_repository.get_by_username(username)
                if existing_username and existing_username.id != user_id:
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }
            
            # Cek apakah email baru sudah digunakan user lain
            if email is not None:
                existing_user = self.user_repository.get_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return {
                        'success': False,
                        'error': 'Email already exists'
                    }
            
            # Validate department if provided
            if department_id is not None:
                department = self.department_repository.get_by_id(department_id)
                if not department:
                    return {
                        'success': False,
                        'error': 'Department not found'
                    }
                
                # Determine the final role (use provided role or existing role)
                final_role = role if role is not None else existing.role
                
                # Check if trying to assign manager role to department that already has a different manager
                if final_role == 'manager' and department.manager_id is not None and department.manager_id != user_id:
                    existing_manager = self.user_repository.get_by_id(department.manager_id)
                    if existing_manager:
                        return {
                            'success': False,
                            'error': f'Department already has a manager: {existing_manager.username}. Only one manager per department is allowed.'
                        }
            
            # Store old values for cleanup
            old_role = existing.role
            old_department_id = existing.department_id
            
            user = self.user_repository.update(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
                department_id=department_id,
                is_active=status
            )
            
            if user:
                # Handle manager_id updates in department table
                
                # Case 1: User was manager and role changed to non-manager - unassign from old department
                if old_role == 'manager' and user.role != 'manager' and old_department_id:
                    old_dept = self.department_repository.get_by_id(old_department_id)
                    if old_dept and old_dept.manager_id == user.id:
                        self.department_repository.update_manager(old_department_id, None)
                
                # Case 2: User was manager and changed department - unassign from old department
                if old_role == 'manager' and user.role == 'manager' and old_department_id != user.department_id and old_department_id:
                    old_dept = self.department_repository.get_by_id(old_department_id)
                    if old_dept and old_dept.manager_id == user.id:
                        self.department_repository.update_manager(old_department_id, None)
                
                # Case 3: User is now manager with department - assign to new department
                if user.role == 'manager' and user.department_id:
                    department = self.department_repository.get_by_id(user.department_id)
                    if department and department.manager_id != user.id:
                        # Update department's manager_id
                        self.department_repository.update_manager(user.department_id, user.id)
                
                user_data = user.to_dict()
                
                # Add department name
                if user.department_id:
                    department = self.department_repository.get_by_id(user.department_id)
                    user_data['department_name'] = department.name if department else None
                else:
                    user_data['department_name'] = None
                
                return {
                    'success': True,
                    'data': user_data
                }
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user(self, user_id: int, current_user_id: int = None) -> Dict:
        """Delete user - cannot delete own account"""
        try:
            # Prevent deleting own account
            if current_user_id and user_id == current_user_id:
                return {
                    'success': False,
                    'error': 'You cannot delete your own account'
                }
            
            success = self.user_repository.delete(user_id)
            if success:
                return {
                    'success': True,
                    'message': 'User deleted successfully'
                }
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_user_by_manager(self, username: str, email: str, password: str,
                               phone: str = None, is_active: bool = True,
                               manager_department_id: int = None) -> Dict:
        """Create user by manager - role automatically set to employee, department from manager"""
        try:
            # Validasi input
            if not username or not email or not password:
                return {
                    'success': False,
                    'error': 'Username, email, and password are required'
                }
            
            # Validate manager has department
            if not manager_department_id:
                return {
                    'success': False,
                    'error': 'Manager does not have a department'
                }
            
            # Validate department exists
            department = self.department_repository.get_by_id(manager_department_id)
            if not department:
                return {
                    'success': False,
                    'error': 'Department not found'
                }
            
            # Check username uniqueness
            existing_username = self.user_repository.get_by_username(username)
            if existing_username:
                return {
                    'success': False,
                    'error': 'Username already taken'
                }
            
            # Check email uniqueness
            existing_email = self.user_repository.get_by_email(email)
            if existing_email:
                return {
                    'success': False,
                    'error': 'Email already taken'
                }
            
            # Create user with role=employee and manager's department_id
            new_user = self.user_repository.create(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role='employee',  # Always employee for manager-created users
                department_id=manager_department_id,  # Manager's department
                is_active=is_active
            )
            
            user_data = new_user.to_dict()
            user_data['department_name'] = department.name
            user_data['total_bookings'] = 0
            
            return {
                'success': True,
                'data': user_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_user_by_manager(self, user_id: int, username: str = None,
                               email: str = None, password: str = None,
                               phone: str = None, is_active: bool = None,
                               manager_department_id: int = None) -> Dict:
        """Update user by manager - can only update users in their department, cannot change role or department"""
        try:
            # Check if user exists
            existing = self.user_repository.get_by_id(user_id)
            if not existing:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Validate manager has department
            if not manager_department_id:
                return {
                    'success': False,
                    'error': 'Manager does not have a department'
                }
            
            # Check if user belongs to manager's department
            if existing.department_id != manager_department_id:
                return {
                    'success': False,
                    'error': 'You can only update employees in your own department'
                }
            
            # Check username uniqueness if provided
            if username is not None:
                existing_username = self.user_repository.get_by_username(username)
                if existing_username and existing_username.id != user_id:
                    return {
                        'success': False,
                        'error': 'Username already taken'
                    }
            
            # Check email uniqueness if provided
            if email is not None:
                existing_email = self.user_repository.get_by_email(email)
                if existing_email and existing_email.id != user_id:
                    return {
                        'success': False,
                        'error': 'Email already taken'
                    }
            
            # Update user - role and department_id are NOT changed
            user = self.user_repository.update(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=None,  # Don't change role
                department_id=None,  # Don't change department
                is_active=is_active
            )
            
            if user:
                user_data = user.to_dict()
                
                # Add department name
                department = self.department_repository.get_by_id(user.department_id)
                user_data['department_name'] = department.name if department else None
                
                # Add total bookings
                total_bookings = self.booking_repository.count_by_user_id(user.id)
                user_data['total_bookings'] = total_bookings
                
                return {
                    'success': True,
                    'data': user_data
                }
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user_by_manager(self, user_id: int, manager_user_id: int,
                               manager_department_id: int = None) -> Dict:
        """Delete user by manager - can only delete users in their department, cannot delete themselves"""
        try:
            # Check if trying to delete themselves
            if user_id == manager_user_id:
                return {
                    'success': False,
                    'error': 'You cannot delete your own account'
                }
            
            # Check if user exists
            existing = self.user_repository.get_by_id(user_id)
            if not existing:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Validate manager has department
            if not manager_department_id:
                return {
                    'success': False,
                    'error': 'Manager does not have a department'
                }
            
            # Check if user belongs to manager's department
            if existing.department_id != manager_department_id:
                return {
                    'success': False,
                    'error': 'You can only delete employees in your own department'
                }
            
            # Prevent deleting managers or superadmins
            if existing.role in ['manager', 'superadmin']:
                return {
                    'success': False,
                    'error': 'You cannot delete users with role manager or superadmin'
                }
            
            # Delete user
            success = self.user_repository.delete(user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Employee deleted successfully'
                }
            return {
                'success': False,
                'error': 'Failed to delete employee'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
