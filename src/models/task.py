from datetime import datetime
from src.config.database import db

class Task(db.Model):
    """Task model"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_user = db.relationship('User', foreign_keys=[user_id], backref='tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        """Convert task object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'priority': self.priority,
            'assignment_id': self.assignment_id,
            'user_id': self.user_id,
            'is_done': self.is_done,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
