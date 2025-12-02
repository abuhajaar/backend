
from flask import request
from src.usecases.stats_usecase import StatsUseCase
from src.utils.response_template import ResponseTemplate

class StatsController:
    """Controller to handle Statistics requests"""
    
    def __init__(self):
        self.usecase = StatsUseCase()
        self.response = ResponseTemplate()
    
    def get_employee_stats(self, user_id):
        """Handler to get employee statistics"""
        try:
            stats = self.usecase.get_employee_stats(user_id)
            return self.response.success(
                data=stats,
                message="Statistics retrieved successfully"
            )
            
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve statistics: {str(e)}"
            )
