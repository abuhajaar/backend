from typing import Dict
from src.repositories.department_repository import DepartmentRepository
from src.repositories.user_repository import UserRepository
from src.config.database import db

class DepartmentUseCase:
    """UseCase for business logic Department"""
    
    def __init__(self):
        self.department_repository = DepartmentRepository()
        self.user_repository = UserRepository()
    
    def get_all_departments(self) -> Dict:
        """Get all departments with total users count"""
        try:
            departments = self.department_repository.get_all()
            departments_list = []
            
            for department in departments:
                department_data = department.to_dict()
                
                # Count total users in this department
                total_users = self.user_repository.count_by_department_id(department.id)
                department_data['total_users'] = total_users
                
                # Get manager info
                if department.manager_id:
                    manager = self.user_repository.get_by_id(department.manager_id)
                    if manager:
                        department_data['manager_name'] = manager.username
                        department_data['manager_email'] = manager.email
                    else:
                        department_data['manager_name'] = None
                        department_data['manager_email'] = None
                else:
                    department_data['manager_name'] = None
                    department_data['manager_email'] = None
                
                departments_list.append(department_data)
            
            return {
                'success': True,
                'data': departments_list,
                'count': len(departments_list)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_department_by_id(self, department_id: int) -> Dict:
        """Get department by ID"""
        try:
            department = self.department_repository.get_by_id(department_id)
            if department:
                department_data = department.to_dict()
                
                # Count total users in this department
                total_users = self.user_repository.count_by_department_id(department.id)
                department_data['total_users'] = total_users
                
                # Get manager info
                if department.manager_id:
                    manager = self.user_repository.get_by_id(department.manager_id)
                    if manager:
                        department_data['manager_name'] = manager.username
                        department_data['manager_email'] = manager.email
                    else:
                        department_data['manager_name'] = None
                        department_data['manager_email'] = None
                else:
                    department_data['manager_name'] = None
                    department_data['manager_email'] = None
                
                return {
                    'success': True,
                    'data': department_data
                }
            return {
                'success': False,
                'error': 'Department not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_department(self, name: str, description: str = None) -> Dict:
        """Create a new department"""
        try:
            # Validasi input
            if not name:
                return {
                    'success': False,
                    'error': 'Name is required'
                }
            
            # Cek apakah nama department sudah ada
            existing_department = self.department_repository.get_by_name(name)
            if existing_department:
                return {
                    'success': False,
                    'error': 'Department name already exists'
                }
            
            # Buat department baru
            new_department = self.department_repository.create(
                name=name, 
                description=description
            )
            department_data = new_department.to_dict()
            department_data['total_users'] = 0
            department_data['manager_name'] = None
            department_data['manager_email'] = None
            
            return {
                'success': True,
                'data': department_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_department(self, department_id: int, name: str = None, description: str = None) -> Dict:
        """Update department"""
        try:
            # Cek apakah nama baru sudah digunakan department lain
            if name is not None:
                existing_department = self.department_repository.get_by_name(name)
                if existing_department and existing_department.id != department_id:
                    return {
                        'success': False,
                        'error': 'Department name already exists'
                    }
            
            department = self.department_repository.update(
                department_id, 
                name=name, 
                description=description
            )
            if department:
                department_data = department.to_dict()
                
                # Count total users in this department
                total_users = self.user_repository.count_by_department_id(department.id)
                department_data['total_users'] = total_users
                
                # Get manager info
                if department.manager_id:
                    manager = self.user_repository.get_by_id(department.manager_id)
                    if manager:
                        department_data['manager_name'] = manager.username
                        department_data['manager_email'] = manager.email
                    else:
                        department_data['manager_name'] = None
                        department_data['manager_email'] = None
                else:
                    department_data['manager_name'] = None
                    department_data['manager_email'] = None
                
                return {
                    'success': True,
                    'data': department_data
                }
            return {
                'success': False,
                'error': 'Department not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_department(self, department_id: int) -> Dict:
        """Delete department"""
        try:
            # Cek apakah masih ada user di department ini
            total_users = self.user_repository.count_by_department_id(department_id)
            if total_users > 0:
                return {
                    'success': False,
                    'error': f'Cannot delete department. Still has {total_users} users assigned.'
                }
            
            success = self.department_repository.delete(department_id)
            if success:
                return {
                    'success': True,
                    'message': 'Department deleted successfully'
                }
            return {
                'success': False,
                'error': 'Department not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
