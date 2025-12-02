from flask import request, jsonify
from src.usecases.floor_usecase import FloorUseCase
from src.utils.response_template import ResponseTemplate

class FloorController:
    """Controller to handle Floor requests"""
    
    def __init__(self):
        self.floor_usecase = FloorUseCase()
        self.response = ResponseTemplate()
    
    def get_floors(self):
        """Handler to get all floors"""
        try:
            result = self.floor_usecase.get_all_floors()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Floors retrieved successfully"
                )
            return self.response.internal_server_error(
                message=result.get('error', 'Failed to retrieve floors')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve floors: {str(e)}"
            )
    
    def get_floor(self, floor_id):
        """Handler to get floor by ID"""
        try:
            result = self.floor_usecase.get_floor_by_id(floor_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Floor retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Floor with ID {floor_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve floor: {str(e)}"
            )
    
    def create_floor(self):
        """Handler to create a new floor"""
        try:
            data = request.get_json()
            
            name = data.get('name') if data else None
            
            result = self.floor_usecase.create_floor(name=name)
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Floor created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create floor')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create floor: {str(e)}"
            )
    
    def update_floor(self, floor_id):
        """Handler to update floor"""
        try:
            data = request.get_json()
            
            name = data.get('name') if data else None
            
            result = self.floor_usecase.update_floor(floor_id=floor_id, name=name)
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Floor updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update floor')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update floor: {str(e)}"
            )
    
    def delete_floor(self, floor_id):
        """Handler to delete floor"""
        try:
            result = self.floor_usecase.delete_floor(floor_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="Floor deleted successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Floor with ID {floor_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete floor: {str(e)}"
            )
