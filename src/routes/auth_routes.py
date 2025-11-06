from flask import Blueprint
from src.controllers.auth_controller import AuthController
from src.utils.jwt_helper import token_required

# Initialize blueprint
auth_routes = Blueprint('auth_routes', __name__)

# Initialize controller
auth_controller = AuthController()

# Define routes
@auth_routes.route('/login', methods=['POST'])
def login():
    """Route for login"""
    print("auth_routes: /login route called")
    return auth_controller.login()

@auth_routes.route('/register', methods=['POST'])
def register():
    """Route for registering a new user"""
    return auth_controller.register()

@auth_routes.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Route for getting current user (protected)"""
    return auth_controller.get_current_user()
