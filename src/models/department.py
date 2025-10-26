from datetime import datetime
from src.config.database import db

class Department(db.Model):
    """Department model"""
    
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id', use_alter=True, name='fk_department_manager'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='dept', lazy=True, foreign_keys='User.department_id')
    manager = db.relationship('User', foreign_keys=[manager_id], post_update=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    def to_dict(self):
        """Convert department object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'manager_id': self.manager_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
