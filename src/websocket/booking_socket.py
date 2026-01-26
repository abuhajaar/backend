from flask import request
from flask_socketio import Namespace, emit, join_room
from src.utils.jwt_helper import decode_access_token
from src.usecases.booking_usecase import BookingUseCase
import logging

logger = logging.getLogger(__name__)

class BookingNamespace(Namespace):
    """WebSocket namespace for bookings"""
    
    def __init__(self, namespace):
        super().__init__(namespace)
        self.booking_usecase = BookingUseCase()
    
    def on_connect(self):
        """Handle client connection to /bookings"""
        emit('connection_response', {'status': 'connected', 'sid': request.sid})
    
    def on_disconnect(self):
        """Handle client disconnection"""
        pass
    
    def on_authenticate(self, data):
        """Authenticate user to bookings channel"""
        try:
            token = data.get('token')
            if not token:
                emit('error', {'message': 'Token required'})
                return
            
            # Verify JWT token
            try:
                payload = decode_access_token(token)
            except Exception as e:
                emit('error', {'message': 'Invalid token'})
                return
            
            if not payload:
                emit('error', {'message': 'Invalid token'})
                return
            
            user_id = payload.get('user_id')
            department_id = payload.get('department_id')
            role = payload.get('role')
            
            # Join user-specific room for their own bookings
            join_room(f'user_{user_id}_bookings')
            
            # Managers also join department room to see all department bookings
            if role == 'manager' and department_id:
                join_room(f'department_{department_id}_bookings')
            
            # Send authentication success
            emit('authenticated', {
                'message': 'Connected to bookings channel',
                'user_id': user_id,
                'role': role
            })
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            emit('error', {'message': str(e)})
    
    def on_get_bookings(self, data):
        """Fetch bookings for the authenticated user"""
        try:
            token = data.get('token')
            if not token:
                emit('error', {'message': 'Token required'})
                return
            
            # Verify JWT token
            payload = decode_access_token(token)
            if not payload:
                emit('error', {'message': 'Invalid token'})
                return
            
            user_id = payload.get('user_id')
            role = payload.get('role')
            department_id = payload.get('department_id')
            
            # Fetch bookings based on role
            if role == 'manager' and department_id:
                # Managers can see all department bookings
                bookings = self.booking_usecase.get_department_bookings(department_id)
            else:
                # Regular users see only their own bookings
                bookings = self.booking_usecase.get_user_bookings(user_id)
            
            # Send bookings data
            emit('bookings_data', {
                'bookings': bookings,
                'count': len(bookings)
            })
            
        except Exception as e:
            logger.error(f"Error fetching bookings: {str(e)}")
            emit('error', {'message': f'Failed to fetch bookings: {str(e)}'})

# Broadcast functions for bookings
def broadcast_booking_created(socketio, booking_data):
    """Broadcast new booking to relevant users"""
    user_id = booking_data.get('user_id')
    department_id = booking_data.get('department_id')
    
    # Broadcast to the user who created the booking
    socketio.emit('created', booking_data,
                 namespace='/bookings',
                 room=f'user_{user_id}_bookings')
    
    # Also broadcast to department managers if department exists
    if department_id:
        socketio.emit('created', booking_data,
                     namespace='/bookings',
                     room=f'department_{department_id}_bookings')

def broadcast_booking_updated(socketio, booking_data):
    """Broadcast booking update to relevant users"""
    user_id = booking_data.get('user_id')
    department_id = booking_data.get('department_id')
    
    # Broadcast to the booking owner
    socketio.emit('updated', booking_data,
                 namespace='/bookings',
                 room=f'user_{user_id}_bookings')
    
    # Also broadcast to department managers
    if department_id:
        socketio.emit('updated', booking_data,
                     namespace='/bookings',
                     room=f'department_{department_id}_bookings')

def broadcast_booking_deleted(socketio, booking_id, user_id, department_id):
    """Broadcast booking deletion to relevant users"""
    # Broadcast to the booking owner
    socketio.emit('deleted', {'id': booking_id},
                 namespace='/bookings',
                 room=f'user_{user_id}_bookings')
    
    # Also broadcast to department managers
    if department_id:
        socketio.emit('deleted', {'id': booking_id},
                     namespace='/bookings',
                     room=f'department_{department_id}_bookings')
