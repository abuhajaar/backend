"""
Routes untuk Statistics
Mendefinisikan endpoint-endpoint statistics
"""
from flask import Blueprint
from src.controllers.stats_controller import StatsController
from src.utils.jwt_helper import token_required

# Create blueprint
stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats_employee')

# Initialize controller
controller = StatsController()

@stats_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_employee_stats(user_id):
    """
    GET /api/stats_employee/:user_id
    Get statistics untuk employee
    Response:
    {
        "user_id": 1,
        "today_bookings": 2,
        "upcoming_bookings": 5,
        "weekly_booking_hours": 8.5,
        "favorite_space": {
            "space_id": 3,
            "space_name": "Meeting Room A",
            "space_type": "meeting_room",
            "booking_count": 10
        }
    }
    """
    return controller.get_employee_stats(user_id)
