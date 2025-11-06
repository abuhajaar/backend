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
    Get statistics for employee by user ID
    """
    return controller.get_employee_stats(user_id)
