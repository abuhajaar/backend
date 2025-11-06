from flask import Blueprint
from src.controllers.health_controller import HealthController

# Initialize blueprint
health_routes = Blueprint('health_routes', __name__)

# Initialize controller
health_controller = HealthController()

# Define routes
@health_routes.route('/health', methods=['GET'])
def health_check():
    """Route for health check"""
    return health_controller.health_check()
