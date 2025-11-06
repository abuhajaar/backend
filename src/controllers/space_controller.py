from flask import jsonify
from src.usecases.space_usecase import SpaceUseCase
from src.utils.response_template import ResponseTemplate

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
