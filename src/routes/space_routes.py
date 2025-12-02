from flask import Blueprint, request
from src.controllers.space_controller import SpaceController
from src.utils.jwt_helper import token_required, role_required

# Create blueprint
space_routes = Blueprint('space', __name__)

# Initialize controller
space_controller = SpaceController()

#Employee endpoints - Get spaces with availability
@space_routes.route('', methods=['GET'])
@token_required
def get_all_spaces():
    """Get all spaces with optional filters"""
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    return space_controller.get_all_spaces(date, start_time, end_time)

@space_routes.route('/<int:space_id>', methods=['GET'])
@token_required
def get_space_by_id(space_id):
    """Get space by ID"""
    return space_controller.get_space_by_id(space_id)



#################################################################################


# Superadmin CRUD endpoints
@space_routes.route('/manage', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_spaces_manage():
    """Get all spaces for management (superadmin only)"""
    return space_controller.get_spaces_for_management()

@space_routes.route('/manage/<int:space_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_space_manage(space_id):
    """Get space by ID for management (superadmin only)"""
    return space_controller.get_space_for_management(space_id)

@space_routes.route('/manage', methods=['POST'])
@token_required
@role_required(['superadmin'])
def create_space():
    """Create new space (superadmin only)"""
    return space_controller.create_space()

@space_routes.route('/manage/<int:space_id>', methods=['PUT'])
@token_required
@role_required(['superadmin'])
def update_space(space_id):
    """Update space (superadmin only)"""
    return space_controller.update_space(space_id)

@space_routes.route('/manage/<int:space_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_space(space_id):
    """Delete space (superadmin only)"""
    return space_controller.delete_space(space_id)
