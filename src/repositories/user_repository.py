from typing import List, Optional
from src.models.user import User
from src.config.database import db

class UserRepository:
    """Repository for User operations"""
    
    def get_all(self) -> List[User]:
        """Get all users from the database"""
        return User.query.all()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def create(self, username: str, email: str, password: str, phone: str = None, 
               role: str = 'employee', department_id: int = None, is_active: bool = True) -> User:
        """Create new user"""
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            role=role,
            department_id=department_id,
            is_active=is_active
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def update(self, user_id: int, username: str = None, email: str = None, 
               password: str = None, phone: str = None, role: str = None, 
               department_id: int = None, is_active: bool = None) -> Optional[User]:
        """Update user"""
        user = self.get_by_id(user_id)
        if user:
            if username is not None:
                user.username = username
            if email is not None:
                user.email = email
            if password is not None:
                user.set_password(password)
            if phone is not None:
                user.phone = phone
            if role is not None:
                user.role = role
            if department_id is not None:
                user.department_id = department_id
            if is_active is not None:
                user.is_active = is_active
            db.session.commit()
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        user = self.get_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    def count_by_department_id(self, department_id: int) -> int:
        """Count total users in a specific department"""
        return User.query.filter_by(department_id=department_id).count()
