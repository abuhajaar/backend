from datetime import datetime
from src.config.database import db

class Amenity(db.Model):
    """Amenity model - fasilitas di setiap space"""
    
    __tablename__ = 'amenities'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50))  # icon identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Amenity {self.name}>'
    
    def to_dict(self):
        """Convert amenity object to dictionary"""
        return {
            'id': self.id,
            'space_id': self.space_id,
            'name': self.name,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
