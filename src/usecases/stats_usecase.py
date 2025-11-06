from src.repositories.stats_repository import StatsRepository

class StatsUseCase:
    """UseCase for business logic Statistics"""
    
    def __init__(self):
        self.repository = StatsRepository()
    
    def get_employee_stats(self, user_id):
        """Get statistics for each employee"""
        # Get all statistics
        today_bookings = self.repository.get_today_bookings_count(user_id)
        upcoming_bookings = self.repository.get_upcoming_bookings_count(user_id)
        weekly_hours = self.repository.get_weekly_booking_hours(user_id)
        favorite_space = self.repository.get_favorite_space(user_id)
        
        # Build response
        stats = {
            'user_id': user_id,
            'today_bookings': today_bookings,
            'upcoming_bookings': upcoming_bookings,
            'weekly_booking_hours': weekly_hours,
            'favorite_space': favorite_space
        }
        
        return stats
