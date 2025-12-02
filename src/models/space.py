from datetime import datetime
from src.config.database import db
from sqlalchemy.dialects.mysql import JSON

class Space(db.Model):
    """Space model - meeting rooms, hot desks, phone booths"""
    
    __tablename__ = 'spaces'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # hot_desk, private_room, meeting_room
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.Integer, db.ForeignKey('floors.id'), nullable=False)
    opening_hours = db.Column(JSON)  # JSON format untuk jam operasional
    max_duration = db.Column(db.Integer)  # dalam menit
    status = db.Column(db.String(20), default='available')  # available, booked, in_maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    amenities = db.relationship('Amenity', backref='space', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='space', lazy=True)
    
    def __repr__(self):
        return f'<Space {self.name}>'
    
    def to_dict(self):
        """Convert space object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'capacity': self.capacity,
            'location': self.location,
            'opening_hours': self.opening_hours,
            'max_duration': self.max_duration,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
