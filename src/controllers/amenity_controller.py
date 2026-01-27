from flask import request, jsonify
from src.usecases.amenity_usecase import AmenityUseCase
from src.utils.response_template import ResponseTemplate

class AmenityController:
    """Controller to handle Amenity requests"""
    
    def __init__(self):
        self.amenity_usecase = AmenityUseCase()
        self.response = ResponseTemplate()
    
    def get_amenities(self):
        """Handler to get all amenities"""
        try:
            result = self.amenity_usecase.get_all_amenities()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Amenities retrieved successfully"
                )
            return self.response.internal_error(
                message=result.get('error', 'Failed to retrieve amenities')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve amenities: {str(e)}"
            )
    
    def get_amenity(self, amenity_id):
        """Handler to get amenity by ID"""
        try:
            result = self.amenity_usecase.get_amenity_by_id(amenity_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Amenity retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Amenity with ID {amenity_id} not found')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve amenity: {str(e)}"
            )
    
    def create_amenity(self):
        """Handler to create a new amenity"""
        try:
            data = request.get_json()
            
            space_id = data.get('space_id') if data else None
            name = data.get('name') if data else None
            icon = data.get('icon') if data else None
            
            result = self.amenity_usecase.create_amenity(
                space_id=space_id,
                name=name,
                icon=icon
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Amenity created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create amenity')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to create amenity: {str(e)}"
            )
    
    def update_amenity(self, amenity_id):
        """Handler to update amenity"""
        try:
            data = request.get_json()
            
            space_id = data.get('space_id') if data else None
            name = data.get('name') if data else None
            icon = data.get('icon') if data else None
            
            result = self.amenity_usecase.update_amenity(
                amenity_id=amenity_id,
                space_id=space_id,
                name=name,
                icon=icon
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Amenity updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update amenity')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to update amenity: {str(e)}"
            )
    
    def delete_amenity(self, amenity_id):
        """Handler to delete amenity"""
        try:
            result = self.amenity_usecase.delete_amenity(amenity_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="Amenity deleted successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Amenity with ID {amenity_id} not found')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to delete amenity: {str(e)}"
            )
