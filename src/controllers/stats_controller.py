
from flask import request
from src.usecases.stats_usecase import StatsUseCase
from src.utils.response_template import ResponseTemplate

class StatsController:
    """Controller to handle Statistics requests"""
    
    def __init__(self):
        self.usecase = StatsUseCase()
        self.response = ResponseTemplate()
    
    def get_user_stats(self):
        """Handler to get user statistics (all roles)"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            user_id = current_user.get('user_id')
            department_id = current_user.get('department_id')
            role = current_user.get('role', 'employee')
            
            result = self.usecase.get_user_stats(user_id, department_id, role)
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Statistics retrieved successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to retrieve statistics')
            )
            
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve statistics: {str(e)}"
            )
