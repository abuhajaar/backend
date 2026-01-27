from flask import request
from flask_socketio import Namespace, emit, join_room, leave_room
from src.utils.jwt_helper import decode_access_token
from src.usecases.announcement_usecase import AnnouncementUseCase
from src.repositories.department_repository import DepartmentRepository
import logging

logger = logging.getLogger(__name__)

class AnnouncementNamespace(Namespace):
    """WebSocket namespace for announcements"""
    
    def __init__(self, namespace):
        super().__init__(namespace)
        self.announcement_usecase = AnnouncementUseCase()
    
    def on_connect(self):
        """Handle client connection to /announcements"""
        emit('connection_response', {'status': 'connected', 'sid': request.sid})
    
    def on_disconnect(self):
        """Handle client disconnection"""
        pass
    
    def on_authenticate(self, data):
        """Authenticate and auto-subscribe to announcements"""
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
            
            # Auto-join rooms
            join_room('global_announcements')
            subscriptions = ['global']
            
            # Superadmin joins ALL department rooms to receive all announcements
            if role == 'superadmin':
                join_room('superadmin_announcements')  # Special room for superadmin broadcasts
                subscriptions.append('superadmin_all')
                # Join all department rooms
                departments = DepartmentRepository.get_all()
                for dept in departments:
                    join_room(f'department_{dept.id}_announcements')
                    subscriptions.append(f'department_{dept.id}')
            elif department_id:
                join_room(f'department_{department_id}_announcements')
                subscriptions.append(f'department_{department_id}')
            
            # Send authentication success
            emit('authenticated', {
                'message': 'Connected to announcements channel',
                'user_id': user_id,
                'role': role,
                'subscribed_to': subscriptions
            })
            
            # Fetch and send initial announcements
            try:
                if role == 'superadmin':
                    # Superadmin gets ALL announcements from all departments
                    from src.repositories.announcement_repository import AnnouncementRepository
                    announcement_repo = AnnouncementRepository()
                    all_announcements = announcement_repo.get_all()
                    announcements = []
                    for ann in all_announcements:
                        ann_dict = {
                            'id': ann.id,
                            'title': ann.title,
                            'content': ann.content,
                            'department_id': ann.department_id,
                            'department_name': ann.department.name if ann.department else 'Company Wide',
                            'created_by': ann.created_by,
                            'is_active': ann.is_active,
                            'created_at': ann.created_at.isoformat() if ann.created_at else None,
                            'updated_at': ann.updated_at.isoformat() if ann.updated_at else None
                        }
                        announcements.append(ann_dict)
                elif role == 'manager' and department_id:
                    result = self.announcement_usecase.get_announcements_for_manager(department_id)
                    announcements = result.get('data', []) if result.get('success') else []
                elif role == 'employee' and department_id:
                    result = self.announcement_usecase.get_announcements_for_manager(department_id)
                    announcements = result.get('data', []) if result.get('success') else []
                else:
                    company_wide = self.announcement_usecase.get_announcements_for_manager(0)
                    announcements = company_wide.get('data', []) if company_wide.get('success') else []
                
                emit('announcements_initial', {
                    'announcements': announcements,
                    'count': len(announcements)
                })
                
            except Exception as e:
                logger.error(f"Error fetching announcements: {str(e)}")
                emit('error', {'message': 'Failed to fetch announcements'})
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            emit('error', {'message': str(e)})

# Broadcast functions for announcements
def broadcast_announcement_created(socketio, announcement_data):
    """Broadcast new announcement to relevant rooms"""
    dept_id = announcement_data.get('department_id')
    room = 'global_announcements' if dept_id is None else f'department_{dept_id}_announcements'
    
    # Broadcast to the specific room (global or department)
    socketio.emit('created', announcement_data, 
                 namespace='/announcements', 
                 room=room)
    
    # Also broadcast to superadmin room if it's a department announcement
    # (superadmin already receives global via global_announcements room)
    if dept_id is not None:
        socketio.emit('created', announcement_data,
                     namespace='/announcements',
                     room='superadmin_announcements')

def broadcast_announcement_updated(socketio, announcement_data):
    """Broadcast announcement update"""
    dept_id = announcement_data.get('department_id')
    room = 'global_announcements' if dept_id is None else f'department_{dept_id}_announcements'
    
    socketio.emit('updated', announcement_data,
                 namespace='/announcements',
                 room=room)
    
    # Also notify superadmin for department announcements
    if dept_id is not None:
        socketio.emit('updated', announcement_data,
                     namespace='/announcements',
                     room='superadmin_announcements')

def broadcast_announcement_deleted(socketio, announcement_id, department_id):
    """Broadcast announcement deletion"""
    room = 'global_announcements' if department_id is None else f'department_{department_id}_announcements'
    
    socketio.emit('deleted', {'id': announcement_id},
                 namespace='/announcements',
                 room=room)
    
    # Also notify superadmin for department announcements
    if department_id is not None:
        socketio.emit('deleted', {'id': announcement_id},
                     namespace='/announcements',
                     room='superadmin_announcements')
