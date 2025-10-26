"""
Routes untuk Space
Define endpoints untuk Space
"""
from flask import Blueprint, request
from src.controllers.space_controller import SpaceController

# Create blueprint
space_routes = Blueprint('space', __name__)

# Initialize controller
space_controller = SpaceController()

@space_routes.route('/spaces', methods=['GET'])
def get_all_spaces():
    """
    Get all spaces with optional filters
    Query params:
    - date: YYYY-MM-DD (optional)
    - start_time: HH:MM (optional)
    - end_time: HH:MM (optional)
    """
    date = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    return space_controller.get_all_spaces(date, start_time, end_time)

@space_routes.route('/spaces/<int:space_id>', methods=['GET'])
def get_space_by_id(space_id):
    """Get space by ID"""
    return space_controller.get_space_by_id(space_id)
