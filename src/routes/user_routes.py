from flask import Blueprint
from src.controllers.user_controller import UserController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
user_routes = Blueprint('user_routes', __name__)

# Initialize controller
user_controller = UserController()

# Superadmin routes
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

# Manager routes
@user_routes.route('/department/my-team', methods=['GET'])
@token_required
@role_required(['manager'])
def get_my_team_users():
    """Route for manager to get users from their department"""
    return user_controller.get_my_team_users()

@user_routes.route('/department/my-team', methods=['POST'])
@token_required
@role_required(['manager'])
def create_team_user():
    """Route for manager to create user in their department"""
    return user_controller.create_team_user()

@user_routes.route('/department/my-team/<int:user_id>', methods=['PUT'])
@token_required
@role_required(['manager'])
def update_team_user(user_id):
    """Route for manager to update user in their department"""
    return user_controller.update_team_user(user_id)

@user_routes.route('/department/my-team/<int:user_id>', methods=['DELETE'])
@token_required
@role_required(['manager'])
def delete_team_user(user_id):
    """Route for manager to delete user in their department"""
    return user_controller.delete_team_user(user_id)
