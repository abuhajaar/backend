from datetime import datetime
from src.config.database import db

class Booking(db.Model):
    """Booking model - user reservations for spaces"""
    
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, cancelled, no_show
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    buffer_min_snapshot = db.Column(db.Integer)
    max_duration_snapshot = db.Column(db.Integer)
    checkin_code = db.Column(db.String(50), unique=True)
    code_valid_from = db.Column(db.DateTime)
    code_valid_to = db.Column(db.DateTime)
    checkin_at = db.Column(db.DateTime, nullable=True)
    checkout_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Booking {self.id} - User:{self.user_id} Space:{self.space_id}>'
    
    def to_dict(self):
        """Convert booking object to dictionary"""
        # Format date dan time dari start_at dan end_at
        date = self.start_at.strftime('%Y-%m-%d') if self.start_at else None
        start_time = self.start_at.strftime('%H:%M') if self.start_at else None
        end_time = self.end_at.strftime('%H:%M') if self.end_at else None
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'space_id': self.space_id,
            'space_name': self.space.name if self.space else 'Unknown',
            'space_type': self.space.type if self.space else 'Unknown',
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'status': self.status,
            'checkin_code': self.checkin_code,
            'code_valid_from': self.code_valid_from.isoformat() if self.code_valid_from else None,
            'code_valid_to': self.code_valid_to.isoformat() if self.code_valid_to else None,
            'checkin_at': self.checkin_at.isoformat() if self.checkin_at else None,
            'checkout_at': self.checkout_at.isoformat() if self.checkout_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
