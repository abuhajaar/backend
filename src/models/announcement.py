from datetime import datetime
from src.config.database import db

class Announcement(db.Model):
    """Announcement model"""
    
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='announcements')
    department = db.relationship('Department', foreign_keys=[department_id], backref='announcements')
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
    
    def to_dict(self):
        """Convert announcement object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'department_id': self.department_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
