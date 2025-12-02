from flask import Blueprint
from src.controllers.department_controller import DepartmentController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
department_routes = Blueprint('department_routes', __name__)

# Initialize controller
department_controller = DepartmentController()

# Define routes
@department_routes.route('', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_departments():
    """Route for getting all departments"""
    return department_controller.get_departments()

@department_routes.route('/<int:department_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_department(department_id):
    """Route for getting department by ID"""
    return department_controller.get_department(department_id)

@department_routes.route('', methods=['POST'])
@token_required
@role_required(['superadmin'])
def create_department():
    """Route for creating a new department"""
    return department_controller.create_department()

@department_routes.route('/<int:department_id>', methods=['PUT'])
@token_required
@role_required(['superadmin'])
def update_department(department_id):
    """Route for updating department"""
    return department_controller.update_department(department_id)

@department_routes.route('/<int:department_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_department(department_id):
    """Route for deleting department"""
    return department_controller.delete_department(department_id)
