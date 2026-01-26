from datetime import datetime, timedelta
import secrets
import string
from src.repositories.booking_repository import BookingRepository
from src.repositories.space_repository import SpaceRepository
from src.repositories.user_repository import UserRepository

class BookingUseCase:
    """UseCase for business logic Booking"""
    
    def __init__(self):
        self.repository = BookingRepository()
        self.space_repository = SpaceRepository()
        self.user_repository = UserRepository()
    
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
        
        for booking in existing_bookings:
            # Cek overlap
            if self._is_overlapping(start_at, end_at, booking.start_at, booking.end_at):
                raise ValueError(
                    f"Booking time conflicts with another booking. "
                    f"Space is already booked from {booking.start_at.strftime('%H:%M')} - {booking.end_at.strftime('%H:%M')}"
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
    
    def get_department_bookings(self, department_id):
        """
        Get all bookings for users in a specific department
        """
        # Get all users in the department
        users = self.user_repository.get_users_by_department(department_id)
        user_ids = [user.id for user in users]
        
        # Get all bookings for these users
        all_bookings = []
        for user_id in user_ids:
            bookings = self.repository.get_bookings_by_user(user_id)
            all_bookings.extend(bookings)
        
        # Sort by created_at descending (newest first)
        all_bookings.sort(key=lambda x: x.created_at, reverse=True)
        
        return [booking.to_dict() for booking in all_bookings]
    
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
    
    # Management methods (superadmin only)
    def get_all_bookings_for_management(self):
        """Get all bookings for management with additional info"""
        try:
            bookings = self.repository.get_all_bookings()
            bookings_data = []
            
            for booking in bookings:
                booking_dict = booking.to_dict()
                
                # Get user info
                user = self.user_repository.get_by_id(booking.user_id)
                booking_dict['username'] = user.username if user else None
                booking_dict['user_email'] = user.email if user else None
                
                # Get space info (already in to_dict but add floor)
                space = self.space_repository.get_by_id(booking.space_id)
                if space:
                    floor = self.space_repository.get_floor_by_id(space.location)
                    booking_dict['floor_name'] = floor.name if floor else None
                
                bookings_data.append(booking_dict)
            
            return {
                'success': True,
                'data': bookings_data,
                'total': len(bookings_data)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_booking_for_management(self, booking_id):
        """Get booking by ID for management with detailed info"""
        try:
            booking = self.repository.find_by_id(booking_id)
            
            if not booking:
                return {
                    'success': False,
                    'error': f'Booking with ID {booking_id} not found'
                }
            
            booking_dict = booking.to_dict()
            
            # Get user info
            user = self.user_repository.get_by_id(booking.user_id)
            booking_dict['username'] = user.username if user else None
            booking_dict['user_email'] = user.email if user else None
            booking_dict['user_phone'] = user.phone if user else None
            
            # Get detailed space info
            space = self.space_repository.get_by_id(booking.space_id)
            if space:
                floor = self.space_repository.get_floor_by_id(space.location)
                booking_dict['floor_name'] = floor.name if floor else None
                booking_dict['space_capacity'] = space.capacity
                booking_dict['space_location'] = space.location
            
            return {
                'success': True,
                'data': booking_dict
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_booking_management(self, user_id, space_id, start_at, end_at, status='active'):
        """Create booking as superadmin (with some validation bypass)"""
        from src.config.database import db
        
        try:
            # Validate input
            if not user_id or not space_id or not start_at or not end_at:
                return {
                    'success': False,
                    'error': 'User ID, space ID, start_at, and end_at are required'
                }
            
            # Parse datetime
            try:
                start_dt = self._parse_datetime(start_at)
                end_dt = self._parse_datetime(end_at)
            except ValueError as e:
                return {
                    'success': False,
                    'error': f'Invalid datetime format: {str(e)}'
                }
            
            # Validate time order
            if start_dt >= end_dt:
                return {
                    'success': False,
                    'error': 'Start time must be earlier than end time'
                }
            
            # Validate user exists
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'error': f'User with ID {user_id} not found'
                }
            
            # Validate space exists
            space = self.space_repository.get_by_id(space_id)
            if not space:
                return {
                    'success': False,
                    'error': f'Space with ID {space_id} not found'
                }
            
            # Validate status
            valid_statuses = ['active', 'checkin', 'finished', 'cancelled']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }
            
            # Generate checkin code
            checkin_code = self._generate_checkin_code()
            code_valid_from = start_dt - timedelta(minutes=15)
            code_valid_to = end_dt + timedelta(minutes=15)
            
            # Create booking
            booking_data = {
                'user_id': user_id,
                'space_id': space_id,
                'status': status,
                'start_at': start_dt,
                'end_at': end_dt,
                'max_duration_snapshot': space.max_duration,
                'checkin_code': checkin_code,
                'code_valid_from': code_valid_from,
                'code_valid_to': code_valid_to
            }
            
            new_booking = self.repository.create_booking(booking_data)
            
            booking_dict = new_booking.to_dict()
            booking_dict['username'] = user.username
            booking_dict['floor_name'] = None
            
            if space:
                floor = self.space_repository.get_floor_by_id(space.location)
                booking_dict['floor_name'] = floor.name if floor else None
            
            return {
                'success': True,
                'data': booking_dict
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_booking_management(self, booking_id, user_id=None, space_id=None, start_at=None, end_at=None, status=None):
        """Update booking (superadmin)"""
        from src.config.database import db
        
        try:
            # Get existing booking
            booking = self.repository.find_by_id(booking_id)
            if not booking:
                return {
                    'success': False,
                    'error': f'Booking with ID {booking_id} not found'
                }
            
            # Validate user if provided
            if user_id is not None:
                user = self.user_repository.get_by_id(user_id)
                if not user:
                    return {
                        'success': False,
                        'error': f'User with ID {user_id} not found'
                    }
            
            # Validate space if provided
            if space_id is not None:
                space = self.space_repository.get_by_id(space_id)
                if not space:
                    return {
                        'success': False,
                        'error': f'Space with ID {space_id} not found'
                    }
            
            # Parse and validate datetime if provided
            start_dt = None
            end_dt = None
            
            if start_at is not None:
                try:
                    start_dt = self._parse_datetime(start_at)
                except ValueError as e:
                    return {
                        'success': False,
                        'error': f'Invalid start_at format: {str(e)}'
                    }
            
            if end_at is not None:
                try:
                    end_dt = self._parse_datetime(end_at)
                except ValueError as e:
                    return {
                        'success': False,
                        'error': f'Invalid end_at format: {str(e)}'
                    }
            
            # Validate time order if both provided
            if start_dt and end_dt and start_dt >= end_dt:
                return {
                    'success': False,
                    'error': 'Start time must be earlier than end time'
                }
            
            # Validate status if provided
            if status is not None:
                valid_statuses = ['active', 'checkin', 'finished', 'cancelled']
                if status not in valid_statuses:
                    return {
                        'success': False,
                        'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                    }
            
            # Update booking
            updated_booking = self.repository.update_booking_management(
                booking_id=booking_id,
                user_id=user_id,
                space_id=space_id,
                start_at=start_dt,
                end_at=end_dt,
                status=status
            )
            
            if updated_booking:
                booking_dict = updated_booking.to_dict()
                
                # Get user info
                user = self.user_repository.get_by_id(updated_booking.user_id)
                booking_dict['username'] = user.username if user else None
                
                # Get floor info
                space = self.space_repository.get_by_id(updated_booking.space_id)
                if space:
                    floor = self.space_repository.get_floor_by_id(space.location)
                    booking_dict['floor_name'] = floor.name if floor else None
                
                return {
                    'success': True,
                    'data': booking_dict
                }
            
            return {
                'success': False,
                'error': 'Failed to update booking'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_booking(self, booking_id):
        """Delete booking"""
        from src.config.database import db
        
        try:
            booking = self.repository.find_by_id(booking_id)
            
            if not booking:
                return {
                    'success': False,
                    'error': f'Booking with ID {booking_id} not found'
                }
            
            self.repository.delete_booking(booking_id)
            
            return {
                'success': True,
                'message': f'Booking with ID {booking_id} deleted successfully'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
