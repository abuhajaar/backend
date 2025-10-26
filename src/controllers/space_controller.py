"""
Controller untuk Space
Menghandle request/response untuk Space endpoints
"""
from flask import jsonify
from src.usecases.space_usecase import SpaceUseCase
from src.utils.response_template import ResponseTemplate

class SpaceController:
    """Controller untuk Space endpoints"""
    
    def __init__(self):
        self.space_usecase = SpaceUseCase()
        self.response = ResponseTemplate()
    
    def get_all_spaces(self, date=None, start_time=None, end_time=None):
        """
        Get all spaces with optional time filters
        Args:
            date: Date in YYYY-MM-DD format (optional)
            start_time: Start time in HH:MM format (optional)
            end_time: End time in HH:MM format (optional)
        Returns: JSON response
        """
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
        """
        Get space by ID
        Args:
            space_id: ID of the space
        Returns: JSON response
        """
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
