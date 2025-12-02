from flask import Blueprint
from src.controllers.user_controller import UserController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
user_routes = Blueprint('user_routes', __name__)

# Initialize controller
user_controller = UserController()

# Define routes
@user_routes.route('', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_users():
    """Route for getting all users"""
    return user_controller.get_users()

@user_routes.route('/<int:user_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_user(user_id):
    """Route for getting user by ID"""
    return user_controller.get_user(user_id)

@user_routes.route('', methods=['POST'])
@token_required
@role_required(['superadmin'])
def create_user():
    """Route for creating a new user"""
    return user_controller.create_user()

@user_routes.route('/<int:user_id>', methods=['PUT'])
@token_required
@role_required(['superadmin'])
def update_user(user_id):
    """Route for updating user"""
    return user_controller.update_user(user_id)

@user_routes.route('/<int:user_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_user(user_id):
    """Route for deleting user"""
    return user_controller.delete_user(user_id)
