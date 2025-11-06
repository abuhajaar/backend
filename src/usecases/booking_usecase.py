from datetime import datetime, timedelta
import secrets
import string
from src.repositories.booking_repository import BookingRepository

class BookingUseCase:
    """UseCase for business logic Booking"""
    
    def __init__(self):
        self.repository = BookingRepository()
    
    def create_booking(self, user_id, space_id, start_at_str, end_at_str):
        """Create new booking with complete validation"""
        # Parse datetime
        try:
            start_at = self._parse_datetime(start_at_str)
            end_at = self._parse_datetime(end_at_str)
        except ValueError as e:
            raise ValueError(f"Format datetime not valid: {str(e)}")
        
        # Validate time
        if start_at >= end_at:
            raise ValueError("Start time must be earlier than end time")
        
        if start_at < datetime.now():
            raise ValueError("Cannot book for a time that has already passed")

        # Get space
        space = self.repository.get_space_by_id(space_id)
        if not space:
            raise ValueError(f"Space with ID {space_id} not found")

        # Check space status
        if space.status != 'available':
            raise ValueError(f"Space is currently {space.status}, cannot be booked")

        # Check blackout date
        target_date = start_at.date()
        blackout = self.repository.check_blackout_date(target_date)
        if blackout:
            raise ValueError(f"Date {target_date} is a holiday: {blackout.title}")

        # Check opening hours
        day_name = start_at.strftime('%a').lower()  # mon, tue, wed, ...
        opening_hours = space.opening_hours
        
        if not opening_hours or day_name not in opening_hours:
            raise ValueError(f"Space does not have operating hours for today")
        
        day_hours = opening_hours[day_name]
        if day_hours is None:
            raise ValueError(f"Space is closed today")

        # Parse opening hours
        open_time = datetime.strptime(day_hours['start'], '%H:%M').time()
        close_time = datetime.strptime(day_hours['end'], '%H:%M').time()

        # Validate booking time within operating hours
        if start_at.time() < open_time or end_at.time() > close_time:
            raise ValueError(f"Booking must be within operating hours {day_hours['start']} - {day_hours['end']}")
        
        # Check maximum duration
        duration_minutes = (end_at - start_at).total_seconds() / 60
        if space.max_duration and duration_minutes > space.max_duration:
            raise ValueError(f"Booking duration ({duration_minutes} minutes) exceeds maximum ({space.max_duration} minutes)")
        
        # Check availability (conflict with other bookings)
        existing_bookings = self.repository.get_bookings_by_space_and_date(space_id, target_date)
        buffer_min = space.buffer_min or 0
        
        for booking in existing_bookings:
            # Apply buffer time
            booking_start_with_buffer = booking.start_at - timedelta(minutes=buffer_min)
            booking_end_with_buffer = booking.end_at + timedelta(minutes=buffer_min)
            
            # Cek overlap
            if self._is_overlapping(start_at, end_at, booking_start_with_buffer, booking_end_with_buffer):
                raise ValueError(
                    f"Booking time conflicts with another booking. "
                    f"Space is already booked from {booking.start_at.strftime('%H:%M')} - {booking.end_at.strftime('%H:%M')} "
                    f"(+{buffer_min} minutes buffer)"
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
        Parse datetime string with various formats
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
        
        raise ValueError(f"Format not recognized: {dt_str}")
    
    def _is_overlapping(self, start1, end1, start2, end2):
        """
        Check if two time intervals overlap
        """
        return start1 < end2 and end1 > start2
    
    def _generate_checkin_code(self):
        """
        Generate random checkin code
        Format: CHK-XXXXXXXX (8 characters random uppercase + digits)
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
            raise ValueError(f"Booking with ID {booking_id} not found")
        
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
        """Update booking status (checkin, checkout, cancel)"""
        # Get booking
        booking = self.repository.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        now = datetime.now()
        update_data = {'updated_at': now}

        # Handle based on action
        if action == 'checkin':
            # Validate status
            if booking.status == 'cancelled':
                raise ValueError("Booking has been cancelled, cannot check in")

            if booking.status == 'checkin':
                raise ValueError("Already checked in")

            if booking.status == 'finished':
                raise ValueError("Booking has finished, cannot check in")

            # Validate checkin code required
            if not checkin_code:
                raise ValueError("Checkin code is required for checkin")

            # Validate checkin code
            if booking.checkin_code != checkin_code:
                raise ValueError("Checkin code is invalid")

            # Validate checkin time
            if now < booking.code_valid_from:
                raise ValueError(
                    f"Checkin cannot be performed yet. "
                    f"Checkin opens at {booking.code_valid_from.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            if now > booking.code_valid_to:
                raise ValueError(
                    f"Checkin time has expired. "
                    f"Checkin is valid until {booking.code_valid_to.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            # Update for checkin
            update_data['status'] = 'checkin'
            update_data['checkin_at'] = now
            
        elif action == 'checkout':
            # Validate status
            if booking.status == 'cancelled':
                raise ValueError("Booking has been cancelled, cannot checkout")

            if booking.status == 'finished':
                raise ValueError("Booking has finished, cannot checkout")

            if booking.status != 'checkin':
                raise ValueError("Must check in before checking out")

            # Update for checkout
            update_data['status'] = 'finished'
            update_data['checkout_at'] = now
            
        elif action == 'cancel':
            # Validate status
            if booking.status == 'cancelled':
                raise ValueError("Booking has been cancelled, cannot cancel again")

            if booking.status == 'checkin':
                raise ValueError("Cannot cancel a booking that has already checked in")

            if booking.status == 'finished':
                raise ValueError("Cannot cancel a booking that has finished")

            # Update for cancel
            update_data['status'] = 'cancelled'
            
        else:
            raise ValueError(f"Action is not valid: {action}. Use: checkin, checkout, or cancel")

        # Update booking
        updated_booking = self.repository.update_booking(booking, update_data)
        
        return updated_booking.to_dict()
