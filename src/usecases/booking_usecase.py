"""
UseCase untuk Booking
Berisi business logic untuk booking operations
"""
from datetime import datetime, timedelta
import secrets
import string
from src.repositories.booking_repository import BookingRepository

class BookingUseCase:
    """UseCase untuk business logic Booking"""
    
    def __init__(self):
        self.repository = BookingRepository()
    
    def create_booking(self, user_id, space_id, start_at_str, end_at_str):
        """
        Create booking baru dengan validasi lengkap
        Args:
            user_id: ID user yang booking
            space_id: ID space yang di-booking
            start_at_str: waktu mulai (ISO format atau YYYY-MM-DD HH:MM:SS)
            end_at_str: waktu selesai (ISO format atau YYYY-MM-DD HH:MM:SS)
        Returns: dict dengan booking data atau raise exception
        """
        # Parse datetime
        try:
            start_at = self._parse_datetime(start_at_str)
            end_at = self._parse_datetime(end_at_str)
        except ValueError as e:
            raise ValueError(f"Format datetime tidak valid: {str(e)}")
        
        # Validasi waktu
        if start_at >= end_at:
            raise ValueError("Waktu mulai harus lebih awal dari waktu selesai")
        
        if start_at < datetime.now():
            raise ValueError("Tidak bisa booking untuk waktu yang sudah lewat")
        
        # Get space
        space = self.repository.get_space_by_id(space_id)
        if not space:
            raise ValueError(f"Space dengan ID {space_id} tidak ditemukan")
        
        # Cek status space
        if space.status != 'available':
            raise ValueError(f"Space sedang {space.status}, tidak bisa dibooking")
        
        # Cek blackout date
        target_date = start_at.date()
        blackout = self.repository.check_blackout_date(target_date)
        if blackout:
            raise ValueError(f"Tanggal {target_date} adalah hari libur: {blackout.title}")
        
        # Cek opening hours
        day_name = start_at.strftime('%a').lower()  # mon, tue, wed, ...
        opening_hours = space.opening_hours
        
        if not opening_hours or day_name not in opening_hours:
            raise ValueError(f"Space tidak memiliki jam operasional untuk hari ini")
        
        day_hours = opening_hours[day_name]
        if day_hours is None:
            raise ValueError(f"Space tutup pada hari ini")
        
        # Parse opening hours
        open_time = datetime.strptime(day_hours['start'], '%H:%M').time()
        close_time = datetime.strptime(day_hours['end'], '%H:%M').time()
        
        # Validasi waktu booking dalam jam operasional
        if start_at.time() < open_time or end_at.time() > close_time:
            raise ValueError(f"Booking harus dalam jam operasional {day_hours['start']} - {day_hours['end']}")
        
        # Cek durasi maksimal
        duration_minutes = (end_at - start_at).total_seconds() / 60
        if space.max_duration and duration_minutes > space.max_duration:
            raise ValueError(f"Durasi booking ({duration_minutes} menit) melebihi maksimal ({space.max_duration} menit)")
        
        # Cek availability (conflict dengan booking lain)
        existing_bookings = self.repository.get_bookings_by_space_and_date(space_id, target_date)
        buffer_min = space.buffer_min or 0
        
        for booking in existing_bookings:
            # Apply buffer time
            booking_start_with_buffer = booking.start_at - timedelta(minutes=buffer_min)
            booking_end_with_buffer = booking.end_at + timedelta(minutes=buffer_min)
            
            # Cek overlap
            if self._is_overlapping(start_at, end_at, booking_start_with_buffer, booking_end_with_buffer):
                raise ValueError(
                    f"Waktu booking bentrok dengan booking lain. "
                    f"Space sudah dibooking dari {booking.start_at.strftime('%H:%M')} - {booking.end_at.strftime('%H:%M')} "
                    f"(+{buffer_min} menit buffer)"
                )
        
        # Generate checkin code
        checkin_code = self._generate_checkin_code()
        
        # Hitung code valid time (15 menit sebelum sampai 15 menit setelah end_at)
        code_valid_from = start_at - timedelta(minutes=15)
        code_valid_to = end_at + timedelta(minutes=15)
        
        # Prepare booking data
        booking_data = {
            'user_id': user_id,
            'space_id': space_id,
            'status': 'active',
            'start_at': start_at,
            'end_at': end_at,
            'buffer_min_snapshot': buffer_min,
            'max_duration_snapshot': space.max_duration,
            'checkin_code': checkin_code,
            'code_valid_from': code_valid_from,
            'code_valid_to': code_valid_to
        }
        
        # Create booking
        booking = self.repository.create_booking(booking_data)
        
        # Return dengan space info
        result = booking.to_dict()
        result['space_name'] = space.name
        result['space_type'] = space.type
        
        return result
    
    def _parse_datetime(self, dt_str):
        """
        Parse datetime string dengan berbagai format
        """
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Format tidak didukung. Gunakan format: YYYY-MM-DD HH:MM:SS atau ISO format")
    
    def _is_overlapping(self, start1, end1, start2, end2):
        """
        Cek apakah dua interval waktu overlap
        """
        return start1 < end2 and end1 > start2
    
    def _generate_checkin_code(self):
        """
        Generate random checkin code
        Format: CHK-XXXXXXXX (8 karakter random uppercase + digits)
        """
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(secrets.choice(chars) for _ in range(8))
        return f"CHK-{random_part}"
    
    def get_booking_by_id(self, booking_id):
        """
        Get booking by ID
        """
        booking = self.repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking dengan ID {booking_id} tidak ditemukan")
        
        return booking.to_dict()
    
    def get_all_bookings(self):
        """
        Get all bookings
        """
        bookings = self.repository.get_all_bookings()
        return [booking.to_dict() for booking in bookings]
    
    def get_user_bookings(self, user_id):
        """
        Get all bookings by user
        """
        bookings = self.repository.get_bookings_by_user(user_id)
        return [booking.to_dict() for booking in bookings]
    
    def update_booking_status(self, booking_id, action, checkin_code=None):
        """
        Update booking status (checkin, checkout, cancel)
        Args:
            booking_id: ID booking
            action: 'checkin' | 'checkout' | 'cancel'
            checkin_code: kode checkin (required untuk checkin)
        Returns: dict dengan booking data yang sudah diupdate
        """
        # Get booking
        booking = self.repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking dengan ID {booking_id} tidak ditemukan")
        
        now = datetime.now()
        update_data = {'updated_at': now}
        
        # Handle berdasarkan action
        if action == 'checkin':
            # Validasi status
            if booking.status == 'cancelled':
                raise ValueError("Booking sudah dibatalkan, tidak bisa checkin")
            
            if booking.status == 'checkin':
                raise ValueError("Sudah melakukan checkin sebelumnya")
            
            if booking.status == 'finished':
                raise ValueError("Booking sudah selesai, tidak bisa checkin")
            
            # Validasi checkin code required
            if not checkin_code:
                raise ValueError("Checkin code wajib diisi untuk checkin")
            
            # Validasi checkin code
            if booking.checkin_code != checkin_code:
                raise ValueError("Kode checkin tidak valid")
            
            # Validasi waktu checkin
            if now < booking.code_valid_from:
                raise ValueError(
                    f"Checkin belum bisa dilakukan. "
                    f"Checkin dibuka mulai {booking.code_valid_from.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            if now > booking.code_valid_to:
                raise ValueError(
                    f"Waktu checkin sudah habis. "
                    f"Checkin berlaku sampai {booking.code_valid_to.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            # Update untuk checkin
            update_data['status'] = 'checkin'
            update_data['checkin_at'] = now
            
        elif action == 'checkout':
            # Validasi status
            if booking.status == 'cancelled':
                raise ValueError("Booking sudah dibatalkan, tidak bisa checkout")
            
            if booking.status == 'finished':
                raise ValueError("Booking sudah selesai sebelumnya")
            
            if booking.status != 'checkin':
                raise ValueError("Harus checkin terlebih dahulu sebelum checkout")
            
            # Update untuk checkout
            update_data['status'] = 'finished'
            update_data['checkout_at'] = now
            
        elif action == 'cancel':
            # Validasi status
            if booking.status == 'cancelled':
                raise ValueError("Booking sudah dibatalkan sebelumnya")
            
            if booking.status == 'checkin':
                raise ValueError("Tidak bisa membatalkan booking yang sudah checkin")
            
            if booking.status == 'finished':
                raise ValueError("Tidak bisa membatalkan booking yang sudah selesai")
            
            # Update untuk cancel
            update_data['status'] = 'cancelled'
            
        else:
            raise ValueError(f"Action tidak valid: {action}. Gunakan: checkin, checkout, atau cancel")
        
        # Update booking
        updated_booking = self.repository.update_booking(booking, update_data)
        
        return updated_booking.to_dict()
