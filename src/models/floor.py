from datetime import datetime
from src.config.database import db

class Floor(db.Model):
    """Floor model"""
    
    __tablename__ = 'floors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    spaces = db.relationship('Space', backref='floor', lazy=True)
    
    def __repr__(self):
        return f'<Floor {self.name}>'
    
    def to_dict(self):
        """Convert floor object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
