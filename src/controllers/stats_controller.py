"""
Controller untuk Statistics
Menghandle HTTP request/response untuk statistics endpoints
"""
from flask import request
from src.usecases.stats_usecase import StatsUseCase
from src.utils.response_template import ResponseTemplate

class StatsController:
    """Controller untuk Statistics operations"""
    
    def __init__(self):
        self.usecase = StatsUseCase()
    
    def get_employee_stats(self, user_id):
        """
        Get employee statistics
        """
        try:
            stats = self.usecase.get_employee_stats(user_id)
            return ResponseTemplate.success(
                data=stats,
                message="Statistics berhasil diambil"
            )
            
        except Exception as e:
            return ResponseTemplate.internal_error(
                message=f"Terjadi kesalahan: {str(e)}"
            )
