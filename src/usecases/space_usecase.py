"""
Use case untuk Space
Menghandle business logic untuk Space
"""
from datetime import datetime, timedelta
from src.repositories.space_repository import SpaceRepository
from src.models.floor import Floor
from src.models.amenity import Amenity
from src.models.booking import Booking

class SpaceUseCase:
    """Use case untuk Space business logic"""
    
    def __init__(self):
        self.space_repository = SpaceRepository()
    
    def get_all_spaces(self, date=None, start_time=None, end_time=None):
        """
        Get all spaces dengan floor name dan amenities
        Filter berdasarkan availability jika date dan time diberikan
        Args:
            date: Date in YYYY-MM-DD format (optional)
            start_time: Start time in HH:MM format (optional)
            end_time: End time in HH:MM format (optional)
        Returns: List of dict dengan space data lengkap
        """
        spaces = self.space_repository.get_all_spaces()
        result = []
        
        # Parse datetime filters if provided
        requested_start = None
        requested_end = None
        check_date = None
        
        if date and start_time and end_time:
            try:
                # Parse date and times
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                # Combine to datetime
                requested_start = datetime.combine(date_obj.date(), start_time_obj)
                requested_end = datetime.combine(date_obj.date(), end_time_obj)
                check_date = date_obj
                
                # Validate
                if requested_end <= requested_start:
                    raise ValueError("End time must be after start time")
                    
            except ValueError as e:
                if "does not match format" in str(e):
                    raise ValueError("Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time")
                raise
        
        for space in spaces:
            # Get floor information
            floor = Floor.query.filter_by(id=space.location).first()
            
            # Get amenities for this space
            amenities = Amenity.query.filter_by(space_id=space.id).all()
            amenities_list = [
                {
                    'id': amenity.id,
                    'name': amenity.name,
                    'icon': amenity.icon
                }
                for amenity in amenities
            ]
            
            # Check availability if time filters provided
            is_available = True
            available_hours = None
            
            if requested_start and requested_end:
                availability_result = self._check_space_availability(
                    space, requested_start, requested_end, check_date
                )
                is_available = availability_result['is_available']
                available_hours = availability_result['available_hours']
                
                # If available_hours is empty/null, space is not available for that day
                if available_hours is not None and len(available_hours) == 0:
                    is_available = False
            
            # Skip space if not available (when filters are applied)
            if requested_start and requested_end and not is_available:
                continue
            
            # Build response
            space_data = {
                'id': space.id,
                'name': space.name,
                'type': space.type,
                'capacity': space.capacity,
                'location': floor.name if floor else None,
                'opening_hours': space.opening_hours,
                'max_duration': space.max_duration,
                'buffer_min': space.buffer_min,
                'status': space.status,
                'amenities': amenities_list,
                'is_available': is_available,
                'created_at': space.created_at.isoformat() if space.created_at else None,
                'updated_at': space.updated_at.isoformat() if space.updated_at else None
            }
            
            # Add available_hours only if date is provided
            if available_hours is not None:
                space_data['available_hours'] = available_hours
            
            result.append(space_data)
        
        return result
    
    def _check_space_availability(self, space, requested_start, requested_end, check_date):
        """
        Check if space is available for the requested time
        Also returns available hours for the entire day
        Args:
            space: Space object
            requested_start: datetime object
            requested_end: datetime object
            check_date: datetime object for the date to check
        Returns: Dict with is_available and available_hours
        """
        result = {
            'is_available': True,
            'available_hours': []
        }
        
        # Check if space is active
        if space.status != 'available':
            result['is_available'] = False
            return result
        
        # Check opening hours for the requested time
        day_of_week = requested_start.strftime('%a').lower()[:3]  # mon, tue, wed, etc
        
        open_time = None
        close_time = None
        
        if space.opening_hours and isinstance(space.opening_hours, dict):
            day_hours = space.opening_hours.get(day_of_week)
            
            if not day_hours:  # Closed on this day
                result['is_available'] = False
                return result
            
            # Parse opening hours
            try:
                open_time = datetime.strptime(day_hours['start'], '%H:%M').time()
                close_time = datetime.strptime(day_hours['end'], '%H:%M').time()
                
                requested_start_time = requested_start.time()
                requested_end_time = requested_end.time()
                
                # Check if requested time is within opening hours
                if requested_start_time < open_time or requested_end_time > close_time:
                    result['is_available'] = False
            except (KeyError, ValueError):
                pass
        
        # Get all bookings for this space on the requested date
        date_start = datetime.combine(check_date.date(), datetime.min.time())
        date_end = datetime.combine(check_date.date(), datetime.max.time())
        
        # Hanya booking dengan status active dan checkin yang block availability
        # cancelled dan finished tidak mempengaruhi availability
        bookings = Booking.query.filter(
            Booking.space_id == space.id,
            Booking.status.in_(['active', 'checkin']),
            Booking.start_at >= date_start,
            Booking.start_at < date_end
        ).all()
        
        # Build available hours for the entire day
        if open_time and close_time:
            available_hours = self._calculate_available_hours(
                space, check_date, open_time, close_time, bookings
            )
            result['available_hours'] = available_hours
            
            # Check if requested time slot is available
            requested_available = self._is_time_slot_available(
                requested_start, requested_end, bookings, space.buffer_min
            )
            
            if not requested_available:
                result['is_available'] = False
        
        return result
    
    def _calculate_available_hours(self, space, check_date, open_time, close_time, bookings):
        """
        Calculate available hours for the entire day
        Args:
            space: Space object
            check_date: datetime object for the date
            open_time: time object for opening
            close_time: time object for closing
            bookings: List of Booking objects
        Returns: List of available time slots
        """
        available_slots = []
        
        # Convert times to datetime for easier calculation
        current_time = datetime.combine(check_date.date(), open_time)
        end_time = datetime.combine(check_date.date(), close_time)
        
        # Sort bookings by start time
        sorted_bookings = sorted(bookings, key=lambda b: b.start_at)
        
        for booking in sorted_bookings:
            # Add buffer time before booking
            booking_start_with_buffer = booking.start_at - timedelta(minutes=space.buffer_min or 0)
            
            # If there's a gap before this booking, add it as available
            if current_time < booking_start_with_buffer:
                available_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': booking_start_with_buffer.strftime('%H:%M')
                })
            
            # Move current time to after this booking (including buffer)
            booking_end_with_buffer = booking.end_at + timedelta(minutes=space.buffer_min or 0)
            current_time = max(current_time, booking_end_with_buffer)
        
        # Add remaining time until closing if available
        if current_time < end_time:
            available_slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M')
            })
        
        return available_slots
    
    def _is_time_slot_available(self, requested_start, requested_end, bookings, buffer_min):
        """
        Check if a specific time slot is available
        Args:
            requested_start: datetime object
            requested_end: datetime object
            bookings: List of Booking objects
            buffer_min: int, buffer minutes
        Returns: Boolean
        """
        buffer_minutes = buffer_min or 0
        
        for booking in bookings:
            # Calculate booking time range with buffer
            booking_start_with_buffer = booking.start_at - timedelta(minutes=buffer_minutes)
            booking_end_with_buffer = booking.end_at + timedelta(minutes=buffer_minutes)
            
            # Check if there's any overlap
            if (requested_start < booking_end_with_buffer and 
                requested_end > booking_start_with_buffer):
                return False
        
        return True
    
    def get_space_by_id(self, space_id):
        """
        Get space by ID dengan floor name dan amenities
        Args:
            space_id: ID of the space
        Returns: Dict with space data or None
        """
        space = self.space_repository.get_space_by_id(space_id)
        
        if not space:
            return None
        
        # Get floor information
        floor = Floor.query.filter_by(id=space.location).first()
        
        # Get amenities for this space
        amenities = Amenity.query.filter_by(space_id=space.id).all()
        amenities_list = [
            {
                'id': amenity.id,
                'name': amenity.name,
                'icon': amenity.icon
            }
            for amenity in amenities
        ]
        
        # Build response
        space_data = {
            'id': space.id,
            'name': space.name,
            'type': space.type,
            'capacity': space.capacity,
            'location': floor.name if floor else None,
            'opening_hours': space.opening_hours,
            'max_duration': space.max_duration,
            'buffer_min': space.buffer_min,
            'status': space.status,
            'amenities': amenities_list,
            'created_at': space.created_at.isoformat() if space.created_at else None,
            'updated_at': space.updated_at.isoformat() if space.updated_at else None
        }
        
        return space_data
