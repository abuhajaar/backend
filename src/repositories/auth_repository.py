from typing import Optional
from src.models.user import User
from src.models.department import Department
from src.config.database import db

class AuthRepository:
    """Repository untuk authentication"""
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    def create_user(self, username: str, email: str, password: str, 
                   phone: str = None, role: str = 'user', 
                   department_id: int = None) -> User:
        """Create new user"""
        user = User(
            username=username,
            email=email,
            phone=phone,
            role=role,
            department_id=department_id,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
