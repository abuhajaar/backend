from datetime import datetime, timedelta
from sqlalchemy import func, and_
from src.models.booking import Booking
from src.models.space import Space
from src.models.user import User
from src.config.database import db

class StatsRepository:
    """Repository for Statistics operations"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """Validate user exists"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_today_bookings_count(user_id):
        """Get today's booking count for a user
        Only bookings with active and checkin status"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        count = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.start_at >= today_start,
            Booking.start_at < today_end,
            Booking.status.in_(['active', 'checkin'])
        ).count()
        
        return count
    
    @staticmethod
    def get_upcoming_bookings_count(user_id):
        """Get upcoming bookings count for a user with active status"""
        tomorrow_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        count = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.start_at >= tomorrow_start,
            Booking.status == 'active'
        ).count()
        
        return count
    
    @staticmethod
    def get_weekly_booking_hours(user_id):
        """Get total hours of bookings for the current week"""
        # Get start of current week (Monday)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)
        
        # Get bookings with checkin and checkout in the current week
        bookings = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.checkin_at.isnot(None),
            Booking.checkout_at.isnot(None),
            Booking.checkin_at >= week_start,
            Booking.checkin_at < week_end
        ).all()
        
        total_hours = 0.0
        for booking in bookings:
            if booking.checkin_at and booking.checkout_at:
                duration = booking.checkout_at - booking.checkin_at
                total_hours += duration.total_seconds() / 3600  # Convert to hours
        
        return round(total_hours, 2)
    
    @staticmethod
    def get_favorite_space(user_id):
        """Get favorite space based on booking count"""
        # Query to get the space with the highest booking count
        result = db.session.query(
            Booking.space_id,
            func.count(Booking.id).label('booking_count')
        ).filter(
            Booking.user_id == user_id
        ).group_by(
            Booking.space_id
        ).order_by(
            func.count(Booking.id).desc()
        ).first()
        
        if not result:
            return None
        
        # Get space details
        space = Space.query.filter_by(id=result.space_id).first()
        
        if not space:
            return None
        
        return {
            'space_id': space.id,
            'space_name': space.name,
            'space_type': space.type,
            'booking_count': result.booking_count
        }
