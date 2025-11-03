"""
Repository untuk Booking
Menghandle data access layer untuk Booking
"""
from datetime import datetime
from sqlalchemy.orm import joinedload
from src.models.booking import Booking
from src.models.space import Space
from src.models.blackout import Blackout
from src.config.database import db

class BookingRepository:
    """Repository untuk operasi database Booking"""
    
    @staticmethod
    def create_booking(booking_data):
        """
        Create booking baru
        Args:
            booking_data: dict dengan data booking
        Returns: Booking object yang baru dibuat
        """
        booking = Booking(**booking_data)
        db.session.add(booking)
        db.session.commit()
        # Refresh untuk load relationship
        db.session.refresh(booking)
        return booking
    
    @staticmethod
    def find_by_id(booking_id):
        """
        Get booking by ID
        Args:
            booking_id: ID of the booking
        Returns: Booking object or None
        """
        return Booking.query.options(joinedload(Booking.space)).filter_by(id=booking_id).first()
    
    @staticmethod
    def get_all_bookings():
        """
        Get all bookings
        Returns: List of Booking objects
        """
        return Booking.query.options(joinedload(Booking.space)).all()
    
    @staticmethod
    def get_bookings_by_user(user_id):
        """
        Get all bookings by user
        Args:
            user_id: ID of the user
        Returns: List of Booking objects
        """
        return Booking.query.options(joinedload(Booking.space)).filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_bookings_by_space_and_date(space_id, target_date):
        """
        Get bookings untuk space tertentu pada tanggal tertentu
        Args:
            space_id: ID of the space
            target_date: datetime.date object
        Returns: List of Booking objects (exclude cancelled)
        """
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
        """
        Cek apakah tanggal termasuk blackout date
        Args:
            target_date: datetime.date object
        Returns: Blackout object jika ada, None jika tidak
        """
        target_datetime = datetime.combine(target_date, datetime.min.time())
        
        return Blackout.query.filter(
            Blackout.start_at <= target_datetime,
            Blackout.end_at >= target_datetime
        ).first()
    
    @staticmethod
    def get_space_by_id(space_id):
        """
        Get space by ID (untuk validasi)
        Args:
            space_id: ID of the space
        Returns: Space object or None
        """
        return Space.query.filter_by(id=space_id).first()
    
    @staticmethod
    def update_booking(booking, update_data):
        """
        Update booking
        Args:
            booking: Booking object
            update_data: dict dengan data yang akan diupdate
        Returns: Updated Booking object
        """
        for key, value in update_data.items():
            if hasattr(booking, key):
                setattr(booking, key, value)
        
        db.session.commit()
        db.session.refresh(booking)
        return booking
    
    @staticmethod
    def find_by_checkin_code(checkin_code):
        """
        Get booking by checkin code
        Args:
            checkin_code: checkin code string
        Returns: Booking object or None
        """
        return Booking.query.options(joinedload(Booking.space)).filter_by(checkin_code=checkin_code).first()
