from typing import List, Dict, Optional
from src.repositories.user_repository import UserRepository
from src.config.database import db

class UserUseCase:
    """UseCase untuk business logic User"""
    
    def __init__(self):
        self.user_repository = UserRepository()
    
    def get_all_users(self) -> Dict:
        """Mendapatkan semua users"""
        try:
            users = self.user_repository.get_all()
            users_list = [user.to_dict() for user in users]
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
        """Mendapatkan user berdasarkan ID"""
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
        """Membuat user baru"""
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
        """Hapus user"""
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
