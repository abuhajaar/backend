
from datetime import datetime, timedelta
from src.repositories.space_repository import SpaceRepository
from src.repositories.floor_repository import FloorRepository
from src.repositories.amenity_repository import AmenityRepository
from src.repositories.booking_repository import BookingRepository
from src.repositories.user_repository import UserRepository
from src.repositories.blackout_repository import BlackoutRepository

class SpaceUseCase:
    """Use case for Space business logic"""
    
    def __init__(self):
        self.space_repository = SpaceRepository()
        self.floor_repository = FloorRepository()
        self.amenity_repository = AmenityRepository()
        self.booking_repository = BookingRepository()
        self.user_repository = UserRepository()
        self.blackout_repository = BlackoutRepository()
    
    def get_all_spaces(self, date=None, start_time=None, end_time=None):
        """Get all spaces with floor name dan amenities"""
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
            floor = self.floor_repository.get_by_id(space.location)
            
            # Get amenities for this space
            amenities = self.amenity_repository.get_by_space_id(space.id)
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
            unavailable_reason = None
            
            if requested_start and requested_end:
                availability_result = self._check_space_availability(
                    space, requested_start, requested_end, check_date
                )
                is_available = availability_result['is_available']
                available_hours = availability_result['available_hours']
                unavailable_reason = availability_result.get('unavailable_reason')
                
                # If available_hours is empty/null, space is not available for that day
                if available_hours is not None and len(available_hours) == 0:
                    is_available = False
                
                # Skip space if opening hours is not available (closed) on requested date
                if availability_result.get('is_closed'):
                    continue
                
                # Skip space if requested time is outside opening hours
                if availability_result.get('outside_hours'):
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
                'status': space.status,
                'amenities': amenities_list,
                'is_available': is_available,
                'created_at': space.created_at.isoformat() if space.created_at else None,
                'updated_at': space.updated_at.isoformat() if space.updated_at else None
            }
            
            # Add available_hours only if date is provided
            if available_hours is not None:
                space_data['available_hours'] = available_hours
            
            # Add unavailable_reason only if date is provided and space is not available
            if requested_start and requested_end:
                space_data['unavailable_reason'] = unavailable_reason
            
            result.append(space_data)
        
        return result
    
    def _check_space_availability(self, space, requested_start, requested_end, check_date):
        """
        Check if space is available for the requested time
        Also returns available hours for the entire day
        """
        result = {
            'is_available': True,
            'available_hours': [],
            'is_closed': False,
            'outside_hours': False,
            'unavailable_reason': None
        }
        
        # Check blackout dates FIRST - office closed means no spaces available
        blackouts = self.blackout_repository.get_active_blackouts(check_date)
        if blackouts:
            result['is_available'] = False
            result['is_closed'] = True
            result['unavailable_reason'] = f"Blackout: {blackouts[0].title}"
            return result
        
        # Check opening hours for the requested time BEFORE status check
        # Office closed (weekend/holiday) takes priority over individual space status
        day_of_week = requested_start.strftime('%a').lower()[:3]  # mon, tue, wed, etc
        
        open_time = None
        close_time = None
        
        if not space.opening_hours or not isinstance(space.opening_hours, dict):
            # No opening hours defined, treat as closed
            result['is_available'] = False
            result['is_closed'] = True
            return result
        
        day_hours = space.opening_hours.get(day_of_week)
        
        if not day_hours:  # Closed on this day (e.g., weekend)
            result['is_available'] = False
            result['is_closed'] = True  # Mark as closed
            return result
        
        # Check if space is active
        if space.status != 'available':
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
                result['outside_hours'] = True  # Mark as outside operating hours
                return result
        except (KeyError, ValueError) as e:
            # Invalid opening hours format, treat as closed
            result['is_available'] = False
            result['is_closed'] = True
            return result
        
        # Get all bookings for this space on the requested date
        date_start = datetime.combine(check_date.date(), datetime.min.time())
        date_end = datetime.combine(check_date.date(), datetime.max.time())
        
        # Get bookings through repository
        all_bookings = self.booking_repository.get_by_space_id(space.id)
        
        # Filter bookings for the specific date and status
        bookings = [
            b for b in all_bookings
            if b.status in ['active', 'checkin']
            and b.start_at >= date_start
            and b.start_at < date_end
        ]
        
        # Build available hours for the entire day
        if open_time and close_time:
            available_hours = self._calculate_available_hours(
                space, check_date, open_time, close_time, bookings
            )
            result['available_hours'] = available_hours
            
            # Check if requested time slot is available
            conflicting_booking = self._find_conflicting_booking(
                requested_start, requested_end, bookings
            )
            
            if conflicting_booking:
                result['is_available'] = False
                # Build unavailable reason with user info
                user = self.user_repository.get_by_id(conflicting_booking.user_id)
                username = user.username if user else "Unknown"
                
                start_time = conflicting_booking.start_at.strftime('%H:%M')
                end_time = conflicting_booking.end_at.strftime('%H:%M')
                
                result['unavailable_reason'] = (
                    f"This space is already booked by {username} "
                    f"from {start_time} to {end_time}"
                )
        
        return result
    
    def _calculate_available_hours(self, space, check_date, open_time, close_time, bookings):
        """Calculate available hours for the entire day"""
        available_slots = []
        
        # Convert times to datetime for easier calculation
        current_time = datetime.combine(check_date.date(), open_time)
        end_time = datetime.combine(check_date.date(), close_time)
        
        # Sort bookings by start time
        sorted_bookings = sorted(bookings, key=lambda b: b.start_at)
        
        for booking in sorted_bookings:
            # If there's a gap before this booking, add it as available
            if current_time < booking.start_at:
                available_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': booking.start_at.strftime('%H:%M')
                })
            
            # Move current time to after this booking
            current_time = max(current_time, booking.end_at)
        
        # Add remaining time until closing if available
        if current_time < end_time:
            available_slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M')
            })
        
        return available_slots
    
    def _find_conflicting_booking(self, requested_start, requested_end, bookings):
        """Find the first booking that conflicts with requested time slot"""
        
        for booking in bookings:
            # Check if there's any overlap
            if (requested_start < booking.end_at and 
                requested_end > booking.start_at):
                return booking
        
        return None
    
    def get_space_by_id(self, space_id):
        """Get space by ID with floor name dan amenities"""
        space = self.space_repository.get_space_by_id(space_id)
        
        if not space:
            return None
        
        # Get floor information
        floor = self.floor_repository.get_by_id(space.location)
        
        # Get amenities for this space
        amenities = self.amenity_repository.get_by_space_id(space.id)
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
            'status': space.status,
            'amenities': amenities_list,
            'created_at': space.created_at.isoformat() if space.created_at else None,
            'updated_at': space.updated_at.isoformat() if space.updated_at else None
        }
        
        return space_data
    
    # Management methods (superadmin only)
    def get_all_spaces_for_management(self):
        """Get all spaces for management with additional info"""
        try:
            spaces = self.space_repository.get_all_spaces()
            spaces_data = []
            
            for space in spaces:
                space_dict = space.to_dict()
                
                # Get floor name
                floor = self.floor_repository.get_by_id(space.location)
                space_dict['floor_name'] = floor.name if floor else None
                
                # Get amenities count
                amenities = self.amenity_repository.get_by_space_id(space.id)
                space_dict['total_amenities'] = len(amenities)
                
                # Get total bookings count
                bookings = self.booking_repository.get_by_space_id(space.id)
                space_dict['total_bookings'] = len(bookings)
                
                spaces_data.append(space_dict)
            
            return {
                'success': True,
                'data': spaces_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_space_for_management(self, space_id):
        """Get space by ID for management"""
        try:
            space = self.space_repository.get_space_by_id(space_id)
            
            if space:
                space_dict = space.to_dict()
                
                # Get floor name
                floor = self.floor_repository.get_by_id(space.location)
                space_dict['floor_name'] = floor.name if floor else None
                
                # Get amenities
                amenities = self.amenity_repository.get_by_space_id(space.id)
                space_dict['amenities'] = [
                    {
                        'id': amenity.id,
                        'name': amenity.name,
                        'icon': amenity.icon
                    } for amenity in amenities
                ]
                
                return {
                    'success': True,
                    'data': space_dict
                }
            return {
                'success': False,
                'error': 'Space not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_space(self, name, type, capacity, location, opening_hours=None, max_duration=None, status='available'):
        """Create a new space"""
        from src.config.database import db
        
        try:
            # Validate input
            if not name or not type or not capacity or not location:
                return {
                    'success': False,
                    'error': 'Name, type, capacity, and location are required'
                }
            
            # Validate type
            valid_types = ['hot_desk', 'private_room', 'meeting_room']
            if type not in valid_types:
                return {
                    'success': False,
                    'error': f'Invalid type. Must be one of: {", ".join(valid_types)}'
                }
            
            # Validate status
            valid_statuses = ['available', 'booked', 'in_maintenance']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }
            
            # Validate floor exists
            floor = self.floor_repository.get_by_id(location)
            if not floor:
                return {
                    'success': False,
                    'error': 'Floor not found'
                }
            
            # Check if space name already exists
            existing_space = self.space_repository.get_by_name(name)
            if existing_space:
                return {
                    'success': False,
                    'error': 'Space with this name already exists'
                }
            
            # Create space
            new_space = self.space_repository.create(
                name=name,
                type=type,
                capacity=capacity,
                location=location,
                opening_hours=opening_hours,
                max_duration=max_duration,
                status=status
            )
            
            space_data = new_space.to_dict()
            space_data['floor_name'] = floor.name
            space_data['total_amenities'] = 0
            space_data['total_bookings'] = 0
            
            return {
                'success': True,
                'data': space_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_space(self, space_id, status=None):
        """Update space status only"""
        from src.config.database import db
        
        try:
            # Validate status is provided
            if status is None:
                return {
                    'success': False,
                    'error': 'Status is required'
                }
            
            # Validate status
            valid_statuses = ['available', 'maintenance']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }
            
            # Update space
            updated_space = self.space_repository.update_status(
                space_id=space_id,
                status=status
            )
            
            if updated_space:
                space_dict = updated_space.to_dict()
                
                # Get floor name
                floor = self.floor_repository.get_by_id(updated_space.location)
                space_dict['floor_name'] = floor.name if floor else None
                
                # Get counts
                amenities = self.amenity_repository.get_by_space_id(updated_space.id)
                space_dict['total_amenities'] = len(amenities)
                
                bookings = self.booking_repository.get_by_space_id(updated_space.id)
                space_dict['total_bookings'] = len(bookings)
                
                return {
                    'success': True,
                    'data': space_dict
                }
            return {
                'success': False,
                'error': 'Space not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_space(self, space_id):
        """Delete space"""
        from src.config.database import db
        
        try:
            # Check if space exists
            space = self.space_repository.get_space_by_id(space_id)
            if not space:
                return {
                    'success': False,
                    'error': 'Space not found'
                }
            
            # Check if space has active bookings
            active_bookings = [b for b in self.booking_repository.get_by_space_id(space_id) 
                             if b.status in ['pending', 'confirmed', 'checked_in']]
            
            if active_bookings:
                return {
                    'success': False,
                    'error': f'Cannot delete space. There are {len(active_bookings)} active booking(s)'
                }
            
            # Delete space (amenities will be cascade deleted)
            success = self.space_repository.delete(space_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Space deleted successfully'
                }
            return {
                'success': False,
                'error': 'Failed to delete space'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
