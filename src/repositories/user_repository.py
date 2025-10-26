from typing import List, Optional
from src.models.user import User
from src.config.database import db

class UserRepository:
    """Repository untuk mengelola data User di database"""
    
    def get_all(self) -> List[User]:
        """Mengambil semua user dari database"""
        return User.query.all()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Mengambil user berdasarkan ID"""
        return User.query.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Mengambil user berdasarkan email"""
        return User.query.filter_by(email=email).first()
    
    def create(self, name: str, email: str) -> User:
        """Membuat user baru"""
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
        """Hapus user"""
        user = self.get_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
