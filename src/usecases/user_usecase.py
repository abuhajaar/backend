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
    
    def create_user(self, name: str, email: str) -> Dict:
        """Create a new user"""
        try:
            # Validasi input
            if not name or not email:
                return {
                    'success': False,
                    'error': 'Name and email are required'
                }
            
            # Cek apakah email sudah ada
            existing_user = self.user_repository.get_by_email(email)
            if existing_user:
                return {
                    'success': False,
                    'error': 'Email already exists'
                }
            
            # Buat user baru
            new_user = self.user_repository.create(name=name, email=email)
            return {
                'success': True,
                'data': new_user.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_user(self, user_id: int, name: str = None, email: str = None) -> Dict:
        """Update user"""
        try:
            # Cek apakah email baru sudah digunakan user lain
            if email:
                existing_user = self.user_repository.get_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return {
                        'success': False,
                        'error': 'Email already exists'
                    }
            
            user = self.user_repository.update(user_id, name=name, email=email)
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
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user(self, user_id: int) -> Dict:
        """Delete user"""
        try:
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
