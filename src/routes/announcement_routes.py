from flask import Blueprint
from src.controllers.announcement_controller import AnnouncementController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
announcement_routes = Blueprint('announcement_routes', __name__)

# Initialize controller
announcement_controller = AnnouncementController()

# Manager routes
@announcement_routes.route('', methods=['GET'])
@token_required
@role_required(['manager'])
def get_announcements():
    """Route for manager to get all announcements"""
    return announcement_controller.get_announcements()

@announcement_routes.route('', methods=['POST'])
@token_required
@role_required(['manager'])
def create_announcement():
    """Route for manager to create announcement"""
    return announcement_controller.create_announcement()

@announcement_routes.route('/<int:announcement_id>', methods=['PUT'])
@token_required
@role_required(['manager'])
def update_announcement(announcement_id):
    """Route for manager to update announcement"""
    return announcement_controller.update_announcement(announcement_id)

@announcement_routes.route('/<int:announcement_id>', methods=['DELETE'])
@token_required
@role_required(['manager'])
def delete_announcement(announcement_id):
    """Route for manager to delete announcement"""
    return announcement_controller.delete_announcement(announcement_id)
