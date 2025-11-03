"""
Repository untuk Statistics
Menghandle data access layer untuk Statistics
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from src.models.booking import Booking
from src.models.space import Space
from src.config.database import db

class StatsRepository:
    """Repository untuk operasi database Statistics"""
    
    @staticmethod
    def get_today_bookings_count(user_id):
        """
        Get jumlah booking hari ini untuk user
        Hanya booking dengan status active dan checkin
        Args:
            user_id: ID of the user
        Returns: int count
        """
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
        """
        Get jumlah booking besok dan seterusnya untuk user
        Args:
            user_id: ID of the user
        Returns: int count
        """
        tomorrow_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        count = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.start_at >= tomorrow_start
        ).count()
        
        return count
    
    @staticmethod
    def get_weekly_booking_hours(user_id):
        """
        Get total jam booking per minggu (berdasarkan checkin_at dan checkout_at)
        Args:
            user_id: ID of the user
        Returns: float total hours
        """
        # Get start of current week (Monday)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)
        
        # Get bookings yang sudah checkin dan checkout di minggu ini
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
        """
        Get space favorit berdasarkan jumlah booking
        Args:
            user_id: ID of the user
        Returns: dict with space info or None
        """
        # Query untuk mendapatkan space dengan booking terbanyak
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
