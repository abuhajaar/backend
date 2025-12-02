from flask import Blueprint
from src.controllers.floor_controller import FloorController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
floor_routes = Blueprint('floor_routes', __name__)

# Initialize controller
floor_controller = FloorController()

# Define routes
@floor_routes.route('', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_floors():
    """Route for getting all floors"""
    return floor_controller.get_floors()

@floor_routes.route('/<int:floor_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_floor(floor_id):
    """Route for getting floor by ID"""
    return floor_controller.get_floor(floor_id)

@floor_routes.route('', methods=['POST'])
@token_required
@role_required(['superadmin'])
def create_floor():
    """Route for creating a new floor"""
    return floor_controller.create_floor()

@floor_routes.route('/<int:floor_id>', methods=['PUT'])
@token_required
@role_required(['superadmin'])
def update_floor(floor_id):
    """Route for updating floor"""
    return floor_controller.update_floor(floor_id)

@floor_routes.route('/<int:floor_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_floor(floor_id):
    """Route for deleting floor"""
    return floor_controller.delete_floor(floor_id)
