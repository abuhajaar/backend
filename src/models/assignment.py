from datetime import datetime
from src.config.database import db

class Assignment(db.Model):
    """Assignment model"""
    
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_assignments')
    department = db.relationship('Department', foreign_keys=[department_id], backref='assignments')
    tasks = db.relationship('Task', backref='assignment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Assignment {self.title}>'
    
    def to_dict(self):
        """Convert assignment object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'department_id': self.department_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
