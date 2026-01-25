from flask import request
from src.usecases.announcement_usecase import AnnouncementUseCase
from src.utils.response_template import ResponseTemplate

class AnnouncementController:
    """Controller to handle Announcement requests"""
    
    def __init__(self):
        self.announcement_usecase = AnnouncementUseCase()
        self.response = ResponseTemplate()
    
    def get_announcements(self):
        """Handler for manager to get all announcements"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            result = self.announcement_usecase.get_announcements_for_manager(manager_department_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Announcements retrieved successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to retrieve announcements')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve announcements: {str(e)}"
            )
    
    def create_announcement(self):
        """Handler for manager to create announcement"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            # Get request body
            data = request.get_json()
            
            result = self.announcement_usecase.create_announcement(
                title=data.get('title'),
                description=data.get('description'),
                created_by=manager_id,
                department_id=data.get('department_id'),
                manager_id=manager_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                # Broadcast to WebSocket clients
                from src.config.socketio import socketio
                from src.websocket.announcement_socket import broadcast_announcement_created
                broadcast_announcement_created(socketio, result['data'])
                
                return self.response.created(
                    data=result['data'],
                    message="Announcement created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create announcement')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create announcement: {str(e)}"
            )
    
    def update_announcement(self, announcement_id):
        """Handler for manager to update announcement"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            # Get request body
            data = request.get_json()
            
            result = self.announcement_usecase.update_announcement(
                announcement_id=announcement_id,
                title=data.get('title'),
                description=data.get('description'),
                department_id=data.get('department_id') if 'department_id' in data else 'NOT_PROVIDED',
                manager_id=manager_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                # Broadcast to WebSocket clients
                from src.config.socketio import socketio
                from src.websocket.announcement_socket import broadcast_announcement_updated
                broadcast_announcement_updated(socketio, result['data'])
                
                return self.response.success(
                    data=result['data'],
                    message="Announcement updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update announcement')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update announcement: {str(e)}"
            )
    
    def delete_announcement(self, announcement_id):
        """Handler for manager to delete announcement"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            # Get announcement before deletion to get department_id for broadcast
            announcement = self.announcement_usecase.get_announcement_by_id(announcement_id)
            department_id = announcement.get('department_id') if announcement else None
            
            result = self.announcement_usecase.delete_announcement(
                announcement_id=announcement_id,
                manager_id=manager_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                # Broadcast to WebSocket clients
                from src.config.socketio import socketio
                from src.websocket.announcement_socket import broadcast_announcement_deleted
                broadcast_announcement_deleted(socketio, announcement_id, department_id)
                
                return self.response.success(
                    data=None,
                    message="Announcement deleted successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to delete announcement')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete announcement: {str(e)}"
            )
