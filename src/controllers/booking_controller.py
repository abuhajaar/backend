from flask import request
from src.usecases.booking_usecase import BookingUseCase
from src.utils.response_template import ResponseTemplate
from src.config.socketio import socketio
from src.websocket.booking_socket import broadcast_booking_created, broadcast_booking_updated, broadcast_booking_deleted
from src.websocket.space_socket import broadcast_space_availability_changed
from datetime import datetime

class BookingController:
    """Controller to handle Booking operations"""
    
    def __init__(self):
        self.usecase = BookingUseCase()
        self.response = ResponseTemplate()
    
    def create_booking(self):
        """Handler to create a new booking"""
        try:
            data = request.get_json()
            
            # Validasi required fields
            required_fields = ['user_id', 'space_id', 'start_at', 'end_at']
            for field in required_fields:
                if field not in data:
                    return self.response.bad_request(
                        message=f"Field '{field}' required"
                    )
            
            # Create booking via usecase
            booking = self.usecase.create_booking(
                user_id=data['user_id'],
                space_id=data['space_id'],
                start_at_str=data['start_at'],
                end_at_str=data['end_at']
            )
            
            # Broadcast WebSocket event to bookings namespace
            broadcast_booking_created(socketio, booking)
            
            # Broadcast space availability change to spaces namespace
            # booking dict has: date, start_time, end_time (from to_dict())
            broadcast_space_availability_changed(
                socketio,
                space_id=booking['space_id'],
                date=booking['date'],
                affected_time_range={
                    'start': booking['start_time'],
                    'end': booking['end_time']
                }
            )
            
            return self.response.created(
                data=booking,
                message="Booking created successfully"
            )
            
        except ValueError as e:
            return self.response.bad_request(
                message=str(e)
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to create booking: {str(e)}"
            )
    
    def get_booking_by_id(self, booking_id):
        """Handler to get booking by ID"""
        try:
            booking = self.usecase.get_booking_by_id(booking_id)
            return self.response.success(
                data=booking,
                message="Booking retrieved successfully"
            )
            
        except ValueError as e:
            return self.response.not_found(message=str(e))
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve booking: {str(e)}"
            )
    
    def get_all_bookings(self):
        """Handler to get all bookings"""
        try:
            bookings = self.usecase.get_all_bookings()
            return self.response.success(
                data=bookings,
                message="Bookings retrieved successfully"
            )
            
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve bookings: {str(e)}"
            )
    
    def get_user_bookings(self, user_id):
        """Handler to get all bookings by user"""
        try:
            bookings = self.usecase.get_user_bookings(user_id)
            return self.response.success(
                data=bookings,
                message="User bookings retrieved successfully"
            )
            
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve user bookings: {str(e)}"
            )
    
    def update_booking_status(self, booking_id):
        """Handler to update booking status (checkin, checkout, cancel)"""
        try:
            data = request.get_json()
            
            # Validasi required field
            if 'status' not in data:
                return self.response.bad_request(
                    message="Field 'status' required (checkin, checkout, or cancel)"
                )
            
            action = data['status']
            checkin_code = data.get('checkin_code')
            
            # Update via usecase
            booking = self.usecase.update_booking_status(
                booking_id=booking_id,
                action=action,
                checkin_code=checkin_code
            )
            
            # Broadcast WebSocket event to bookings namespace
            broadcast_booking_updated(socketio, booking)
            
            # Broadcast space availability change if booking is cancelled or checked out
            if action in ['cancel', 'checkout']:
                # booking dict has 'date', 'start_time', 'end_time' from to_dict()
                broadcast_space_availability_changed(
                    socketio,
                    space_id=booking['space_id'],
                    date=booking['date'],
                    affected_time_range={
                        'start': booking['start_time'],
                        'end': booking['end_time']
                    }
                )

            # Response message based on action
            messages = {
                'checkin': 'Check-in successful',
                'checkout': 'Check-out successful',
                'cancel': 'Booking cancelled successfully'
            }
            
            return self.response.success(
                data=booking,
                message=messages.get(action, 'Booking status updated successfully')
            )
            
        except ValueError as e:
            return self.response.bad_request(
                message=str(e)
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to update booking status: {str(e)}"
            )
    
    # Management endpoints (superadmin only)
    def get_bookings_for_management(self):
        """Handler to get all bookings for management"""
        try:
            result = self.usecase.get_all_bookings_for_management()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Bookings retrieved successfully"
                )
            return self.response.internal_error(
                message=result.get('error', 'Failed to retrieve bookings')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve bookings: {str(e)}"
            )
    
    def get_booking_for_management(self, booking_id):
        """Handler to get booking by ID for management"""
        try:
            result = self.usecase.get_booking_for_management(booking_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Booking retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Booking with ID {booking_id} not found')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve booking: {str(e)}"
            )
    
    def create_booking_management(self):
        """Handler to create booking as superadmin"""
        try:
            data = request.get_json()
            
            user_id = data.get('user_id') if data else None
            space_id = data.get('space_id') if data else None
            start_at = data.get('start_at') if data else None
            end_at = data.get('end_at') if data else None
            status = data.get('status', 'active') if data else 'active'
            
            result = self.usecase.create_booking_management(
                user_id=user_id,
                space_id=space_id,
                start_at=start_at,
                end_at=end_at,
                status=status
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Booking created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create booking')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to create booking: {str(e)}"
            )
    
    def update_booking_management(self, booking_id):
        """Handler to update booking"""
        try:
            data = request.get_json()
            
            user_id = data.get('user_id') if data else None
            space_id = data.get('space_id') if data else None
            start_at = data.get('start_at') if data else None
            end_at = data.get('end_at') if data else None
            status = data.get('status') if data else None
            
            result = self.usecase.update_booking_management(
                booking_id=booking_id,
                user_id=user_id,
                space_id=space_id,
                start_at=start_at,
                end_at=end_at,
                status=status
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Booking updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update booking')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to update booking: {str(e)}"
            )
    
    def delete_booking(self, booking_id):
        """Handler to delete booking"""
        try:
            result = self.usecase.delete_booking(booking_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="Booking deleted successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Booking with ID {booking_id} not found')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to delete booking: {str(e)}"
            )
