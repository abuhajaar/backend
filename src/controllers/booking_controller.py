"""
Controller untuk Booking
Menghandle HTTP request/response untuk booking endpoints
"""
from flask import request
from src.usecases.booking_usecase import BookingUseCase
from src.utils.response_template import ResponseTemplate

class BookingController:
    """Controller untuk Booking operations"""
    
    def __init__(self):
        self.usecase = BookingUseCase()
    
    def create_booking(self):
        """Handler to create a new booking"""
        try:
            data = request.get_json()
            
            # Validasi required fields
            required_fields = ['user_id', 'space_id', 'start_at', 'end_at']
            for field in required_fields:
                if field not in data:
                    return ResponseTemplate.bad_request(
                        message=f"Field '{field}' required"
                    )
            
            # Create booking via usecase
            booking = self.usecase.create_booking(
                user_id=data['user_id'],
                space_id=data['space_id'],
                start_at_str=data['start_at'],
                end_at_str=data['end_at']
            )
            
            return ResponseTemplate.created(
                data=booking,
                message="Booking created successfully"
            )
            
        except ValueError as e:
            return ResponseTemplate.bad_request(
                message=str(e)
            )
        except Exception as e:
            return ResponseTemplate.internal_error(
                message=f"An error occurred: {str(e)}"
            )
    
    def get_booking_by_id(self, booking_id):
        """Handler to get booking by ID"""
        try:
            booking = self.usecase.get_booking_by_id(booking_id)
            return ResponseTemplate.success(data=booking)
            
        except ValueError as e:
            return ResponseTemplate.not_found(message=str(e))
        except Exception as e:
            return ResponseTemplate.internal_error(
                message=f"An error occurred: {str(e)}"
            )
    
    def get_all_bookings(self):
        """Handler to get all bookings"""
        try:
            bookings = self.usecase.get_all_bookings()
            return ResponseTemplate.success(
                data=bookings,
                message=f"Found {len(bookings)} bookings"
            )
            
        except Exception as e:
            return ResponseTemplate.internal_error(
                message=f"An error occurred: {str(e)}"
            )
    
    def get_user_bookings(self, user_id):
        """Handler to get all bookings by user"""
        try:
            bookings = self.usecase.get_user_bookings(user_id)
            return ResponseTemplate.success(
                data=bookings,
                message=f"Found {len(bookings)} bookings for user {user_id}"
            )
            
        except Exception as e:
            return ResponseTemplate.internal_error(
                message=f"An error occurred: {str(e)}"
            )
    
    def update_booking_status(self, booking_id):
        """Handler to update booking status (checkin, checkout, cancel)"""
        try:
            data = request.get_json()
            
            # Validasi required field
            if 'status' not in data:
                return ResponseTemplate.bad_request(
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

            # Response message based on action
            messages = {
                'checkin': 'Checkin successful',
                'checkout': 'Checkout successful',
                'cancel': 'Booking successfully canceled'
            }
            
            return ResponseTemplate.success(
                data=booking,
                message=messages.get(action, 'Booking status successfully updated')
            )
            
        except ValueError as e:
            return ResponseTemplate.bad_request(
                message=str(e)
            )
        except Exception as e:
            return ResponseTemplate.internal_error(
                message=f"An error occurred: {str(e)}"
            )
