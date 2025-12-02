from flask import Blueprint, request
from src.controllers.blackout_controller import BlackoutController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
blackout_routes = Blueprint('blackout_routes', __name__)

# Initialize controller
blackout_controller = BlackoutController()

# Define routes
@blackout_routes.route('', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_blackouts():
    """Route for getting all blackouts"""
    return blackout_controller.get_blackouts()

@blackout_routes.route('/<int:blackout_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_blackout(blackout_id):
    """Route for getting blackout by ID"""
    return blackout_controller.get_blackout(blackout_id)

@blackout_routes.route('', methods=['POST'])
@token_required
@role_required(['superadmin'])
def create_blackout():
    """Route for creating a new blackout"""
    # Get current user from token
    current_user = request.current_user
    return blackout_controller.create_blackout(current_user)

@blackout_routes.route('/<int:blackout_id>', methods=['PUT'])
@token_required
@role_required(['superadmin'])
def update_blackout(blackout_id):
    """Route for updating blackout"""
    return blackout_controller.update_blackout(blackout_id)

@blackout_routes.route('/<int:blackout_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_blackout(blackout_id):
    """Route for deleting blackout"""
    return blackout_controller.delete_blackout(blackout_id)
