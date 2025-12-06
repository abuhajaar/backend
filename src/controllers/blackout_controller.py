from flask import request, jsonify
from src.usecases.blackout_usecase import BlackoutUseCase
from src.utils.response_template import ResponseTemplate

class BlackoutController:
    """Controller to handle Blackout requests"""
    
    def __init__(self):
        self.blackout_usecase = BlackoutUseCase()
        self.response = ResponseTemplate()
    
    def get_blackouts(self):
        """Handler to get all blackouts"""
        try:
            result = self.blackout_usecase.get_all_blackouts()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Blackouts berhasil diambil"
                )
            return self.response.internal_server_error(
                message=result.get('error', 'Failed to retrieve blackouts')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve blackouts: {str(e)}"
            )
    
    def get_blackout(self, blackout_id):
        """Handler to get blackout by ID"""
        try:
            result = self.blackout_usecase.get_blackout_by_id(blackout_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Blackout berhasil diambil"
                )
            return self.response.not_found(
                message=result.get('error', f'Blackout with ID {blackout_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve blackout: {str(e)}"
            )
    
    def create_blackout(self, current_user):
        """Handler to create a new blackout"""
        try:
            data = request.get_json()
            
            title = data.get('title') if data else None
            description = data.get('description') if data else None
            start_at = data.get('start_at') if data else None
            end_at = data.get('end_at') if data else None
            created_by = current_user.get('user_id')  # From JWT token
            
            result = self.blackout_usecase.create_blackout(
                title=title,
                description=description,
                start_at=start_at,
                end_at=end_at,
                created_by=created_by
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Blackout berhasil dibuat"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create blackout')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create blackout: {str(e)}"
            )
    
    def update_blackout(self, blackout_id):
        """Handler to update blackout"""
        try:
            data = request.get_json()
            
            title = data.get('title') if data else None
            description = data.get('description') if data else None
            start_at = data.get('start_at') if data else None
            end_at = data.get('end_at') if data else None
            
            result = self.blackout_usecase.update_blackout(
                blackout_id=blackout_id,
                title=title,
                description=description,
                start_at=start_at,
                end_at=end_at
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Blackout berhasil diupdate"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update blackout')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update blackout: {str(e)}"
            )
    
    def delete_blackout(self, blackout_id):
        """Handler to delete blackout"""
        try:
            result = self.blackout_usecase.delete_blackout(blackout_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="Blackout berhasil dihapus"
                )
            return self.response.not_found(
                message=result.get('error', f'Blackout with ID {blackout_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete blackout: {str(e)}"
            )
