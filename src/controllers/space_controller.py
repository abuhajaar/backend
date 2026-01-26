from flask import jsonify, request
from src.usecases.space_usecase import SpaceUseCase
from src.utils.response_template import ResponseTemplate
from src.config.socketio import socketio
from src.websocket.space_socket import broadcast_space_created, broadcast_space_updated, broadcast_space_deleted

class SpaceController:
    """Controller to handle Space requests"""
    
    def __init__(self):
        self.space_usecase = SpaceUseCase()
        self.response = ResponseTemplate()
    
    def get_all_spaces(self, date=None, start_time=None, end_time=None):
        """Handler to get all spaces with optional time filters"""
        try:
            spaces = self.space_usecase.get_all_spaces(date, start_time, end_time)
            return self.response.success(
                data=spaces,
                message="Spaces retrieved successfully"
            )
        except ValueError as e:
            return self.response.bad_request(
                message=str(e)
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve spaces: {str(e)}"
            )
    
    def get_space_by_id(self, space_id):
        """Handler to get space by ID"""
        try:
            space = self.space_usecase.get_space_by_id(space_id)
            
            if not space:
                return self.response.not_found(
                    message=f"Space with ID {space_id} not found"
                )
            
            return self.response.success(
                data=space,
                message="Space retrieved successfully"
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve space: {str(e)}"
            )
    
    # Management endpoints (superadmin only)
    def get_spaces_for_management(self):
        """Handler to get all spaces for management"""
        try:
            result = self.space_usecase.get_all_spaces_for_management()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Spaces retrieved successfully"
                )
            return self.response.internal_server_error(
                message=result.get('error', 'Failed to retrieve spaces')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve spaces: {str(e)}"
            )
    
    def get_space_for_management(self, space_id):
        """Handler to get space by ID for management"""
        try:
            result = self.space_usecase.get_space_for_management(space_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Space retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Space with ID {space_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve space: {str(e)}"
            )
    
    def create_space(self):
        """Handler to create a new space"""
        try:
            data = request.get_json()
            
            name = data.get('name') if data else None
            type = data.get('type') if data else None
            capacity = data.get('capacity') if data else None
            location = data.get('location') if data else None
            opening_hours = data.get('opening_hours') if data else None
            max_duration = data.get('max_duration') if data else None
            status = data.get('status', 'available') if data else 'available'
            
            result = self.space_usecase.create_space(
                name=name,
                type=type,
                capacity=capacity,
                location=location,
                opening_hours=opening_hours,
                max_duration=max_duration,
                status=status
            )
            
            if result['success']:
                # Broadcast WebSocket event
                broadcast_space_created(socketio, result['data'])
                
                return self.response.created(
                    data=result['data'],
                    message="Space created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create space')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create space: {str(e)}"
            )
    
    def update_space(self, space_id):
        """Handler to update space status"""
        try:
            data = request.get_json()
            
            status = data.get('status') if data else None
            
            result = self.space_usecase.update_space(
                space_id=space_id,
                status=status
            )
            
            if result['success']:
                # Broadcast WebSocket event
                broadcast_space_updated(socketio, result['data'])
                
                return self.response.success(
                    data=result['data'],
                    message="Status space updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update space status')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update space status: {str(e)}"
            )
    
    def delete_space(self, space_id):
        """Handler to delete space"""
        try:
            result = self.space_usecase.delete_space(space_id)
            if result['success']:
                # Broadcast WebSocket event
                broadcast_space_deleted(socketio, space_id)
                
                return self.response.success(
                    data=result.get('data'),
                    message="Space deleted successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Space with ID {space_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete space: {str(e)}"
            )
