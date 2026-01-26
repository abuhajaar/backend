from flask import request
from flask_socketio import Namespace, emit, join_room
from src.utils.jwt_helper import decode_access_token
from src.usecases.space_usecase import SpaceUseCase
import logging

logger = logging.getLogger(__name__)

class SpaceNamespace(Namespace):
    """WebSocket namespace for spaces"""
    
    def __init__(self, namespace):
        super().__init__(namespace)
        self.space_usecase = SpaceUseCase()
    
    def on_connect(self):
        """Handle client connection to /spaces"""
        emit('connection_response', {'status': 'connected', 'sid': request.sid})
    
    def on_disconnect(self):
        """Handle client disconnection"""
        pass
    
    def on_authenticate(self, data):
        """Authenticate user to spaces channel"""
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
            role = payload.get('role')
            
            # All authenticated users join global spaces room
            join_room('spaces_updates')
            
            # Send authentication success
            emit('authenticated', {
                'message': 'Connected to spaces channel',
                'user_id': user_id,
                'role': role
            })
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            emit('error', {'message': str(e)})
    
    def on_get_spaces(self, data):
        """Fetch spaces with optional filters (date, start_time, end_time)"""
        try:
            # Extract filters from data
            date = data.get('date') if data else None
            start_time = data.get('start_time') if data else None
            end_time = data.get('end_time') if data else None
            
            # Get spaces using existing usecase (with availability calculation)
            spaces = self.space_usecase.get_all_spaces(date, start_time, end_time)
            
            # Send spaces data
            emit('spaces_data', {
                'spaces': spaces,
                'count': len(spaces),
                'filters': {
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time
                }
            })
            
        except ValueError as e:
            # Validation errors (invalid date/time format, etc.)
            emit('error', {'message': str(e)})
        except Exception as e:
            logger.error(f"Error fetching spaces: {str(e)}")
            emit('error', {'message': f'Failed to fetch spaces: {str(e)}'})

# Broadcast functions for spaces
def broadcast_space_created(socketio, space_data):
    """Broadcast new space creation to all users"""
    socketio.emit('created', space_data, 
                 namespace='/spaces', 
                 room='spaces_updates')

def broadcast_space_updated(socketio, space_data):
    """Broadcast space update to all users"""
    socketio.emit('updated', space_data,
                 namespace='/spaces',
                 room='spaces_updates')

def broadcast_space_deleted(socketio, space_id):
    """Broadcast space deletion to all users"""
    socketio.emit('deleted', {'id': space_id},
                 namespace='/spaces',
                 room='spaces_updates')
