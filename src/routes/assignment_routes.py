from flask import Blueprint
from src.controllers.assignment_controller import AssignmentController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
assignment_routes = Blueprint('assignment_routes', __name__)

# Initialize controller
assignment_controller = AssignmentController()

# Manager routes
@assignment_routes.route('', methods=['GET'])
@token_required
@role_required(['manager'])
def get_assignments():
    """Route for manager to get all assignments for their department"""
    return assignment_controller.get_assignments()

@assignment_routes.route('', methods=['POST'])
@token_required
@role_required(['manager'])
def create_assignment():
    """Route for manager to create assignment"""
    return assignment_controller.create_assignment()

@assignment_routes.route('/<int:assignment_id>', methods=['PUT'])
@token_required
@role_required(['manager'])
def update_assignment(assignment_id):
    """Route for manager to update assignment"""
    return assignment_controller.update_assignment(assignment_id)

@assignment_routes.route('/<int:assignment_id>', methods=['DELETE'])
@token_required
@role_required(['manager'])
def delete_assignment(assignment_id):
    """Route for manager to delete assignment"""
    return assignment_controller.delete_assignment(assignment_id)
