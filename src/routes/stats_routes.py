"""
Routes untuk Statistics
Mendefinisikan endpoint-endpoint statistics
"""
from flask import Blueprint
from src.controllers.stats_controller import StatsController
from src.utils.jwt_helper import token_required

# Create blueprint
stats_bp = Blueprint('stats', __name__)

# Initialize controller
controller = StatsController()

@stats_bp.route('', methods=['GET'])
@token_required
def get_user_stats():
    """
    GET /api/stats_employee
    Get statistics for current user (all roles)
    Includes: announcements, weekly booking hours, favorite space, and todo list
    """
    return controller.get_user_stats()
