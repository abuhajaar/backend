from flask import Blueprint
from src.controllers.amenity_controller import AmenityController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
amenity_routes = Blueprint('amenity_routes', __name__)

# Initialize controller
amenity_controller = AmenityController()

# Define routes
@amenity_routes.route('', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_amenities():
    """Route for getting all amenities"""
    return amenity_controller.get_amenities()

@amenity_routes.route('/<int:amenity_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_amenity(amenity_id):
    """Route for getting amenity by ID"""
    return amenity_controller.get_amenity(amenity_id)

@amenity_routes.route('', methods=['POST'])
@token_required
@role_required(['superadmin'])
def create_amenity():
    """Route for creating a new amenity"""
    return amenity_controller.create_amenity()

@amenity_routes.route('/<int:amenity_id>', methods=['PUT'])
@token_required
@role_required(['superadmin'])
def update_amenity(amenity_id):
    """Route for updating amenity"""
    return amenity_controller.update_amenity(amenity_id)

@amenity_routes.route('/<int:amenity_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_amenity(amenity_id):
    """Route for deleting amenity"""
    return amenity_controller.delete_amenity(amenity_id)
