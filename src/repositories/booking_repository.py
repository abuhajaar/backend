from datetime import datetime
from sqlalchemy.orm import joinedload
from src.models.booking import Booking
from src.models.space import Space
from src.models.blackout import Blackout
from src.config.database import db

class BookingRepository:
    """Repository for Booking operations"""
    
    @staticmethod
    def create_booking(booking_data):
        """Create new booking"""
        booking = Booking(**booking_data)
        db.session.add(booking)
        db.session.commit()
        # Refresh to load relationships
        db.session.refresh(booking)
        return booking
    
    @staticmethod
    def find_by_id(booking_id):
        """Get booking by ID"""
        return Booking.query.options(joinedload(Booking.space)).filter_by(id=booking_id).first()
    
    @staticmethod
    def get_all_bookings():
        """Get all bookings"""
        return Booking.query.options(joinedload(Booking.space)).all()
    
    @staticmethod
    def get_bookings_by_user(user_id):
        """Get all bookings by user"""
        return Booking.query.options(joinedload(Booking.space)).filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_bookings_by_space_and_date(space_id, target_date):
        """Get bookings for a specific space on a specific date"""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        return Booking.query.filter(
            Booking.space_id == space_id,
            Booking.status != 'cancelled',
            Booking.start_at >= start_of_day,
            Booking.start_at <= end_of_day
        ).all()
    
    @staticmethod
    def check_blackout_date(target_date):
        """Check if the date falls within a blackout period"""
        target_datetime = datetime.combine(target_date, datetime.min.time())
        
        return Blackout.query.filter(
            Blackout.start_at <= target_datetime,
            Blackout.end_at >= target_datetime
        ).first()
    
    @staticmethod
    def get_space_by_id(space_id):
        """Get space by ID (for validation)"""
        return Space.query.filter_by(id=space_id).first()
    
    @staticmethod
    def update_booking(booking, update_data):
        """Update booking"""
        for key, value in update_data.items():
            if hasattr(booking, key):
                setattr(booking, key, value)
        
        db.session.commit()
        db.session.refresh(booking)
        return booking
    
    @staticmethod
    def find_by_checkin_code(checkin_code):
        """Get booking by checkin code"""
        return Booking.query.options(joinedload(Booking.space)).filter_by(checkin_code=checkin_code).first()
