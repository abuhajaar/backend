from src.models.department import Department
from src.config.database import db

class DepartmentRepository:
    """Repository for Department operations"""
    
    @staticmethod
    def get_all():
        """Get all departments"""
        return Department.query.all()
    
    @staticmethod
    def get_by_id(department_id):
        """Get department by ID"""
        return Department.query.filter_by(id=department_id).first()
    
    @staticmethod
    def get_by_name(name):
        """Get department by name"""
        return Department.query.filter_by(name=name).first()
    
    @staticmethod
    def create(name, description=None):
        """Create new department"""
        department = Department(name=name, description=description)
        db.session.add(department)
        db.session.commit()
        db.session.refresh(department)
        return department
    
    @staticmethod
    def update(department_id, name=None, description=None):
        """Update department"""
        department = Department.query.filter_by(id=department_id).first()
        
        if not department:
            return None
        
        if name is not None:
            department.name = name
        if description is not None:
            department.description = description
        
        db.session.commit()
        db.session.refresh(department)
        return department
    
    @staticmethod
    def update_manager(department_id, manager_id):
        """Update department manager_id (can be None to unassign)"""
        department = Department.query.filter_by(id=department_id).first()
        
        if not department:
            return None
        
        department.manager_id = manager_id
        db.session.commit()
        db.session.refresh(department)
        return department
    
    @staticmethod
    def delete(department_id):
        """Delete department"""
        department = Department.query.filter_by(id=department_id).first()
        
        if not department:
            return False
        
        db.session.delete(department)
        db.session.commit()
        return True
