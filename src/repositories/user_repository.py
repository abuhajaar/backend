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
    
    def create(self, name: str, email: str) -> User:
        """Create new user"""
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def update(self, user_id: int, name: str = None, email: str = None) -> Optional[User]:
        """Update user"""
        user = self.get_by_id(user_id)
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
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
