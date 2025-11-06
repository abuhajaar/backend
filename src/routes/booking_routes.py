from flask import Blueprint
from src.controllers.booking_controller import BookingController
from src.utils.jwt_helper import token_required

# Create blueprint
booking_bp = Blueprint('booking', __name__, url_prefix='/api/bookings')

# Initialize controller
controller = BookingController()

@booking_bp.route('', methods=['POST'])
@token_required
def create_booking():
    """
    POST /api/bookings
    Create new booking
    """
    return controller.create_booking()

@booking_bp.route('', methods=['GET'])
@token_required
def get_all_bookings():
    """
    GET /api/bookings
    Get all bookings
    """
    return controller.get_all_bookings()

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@token_required
def get_booking_by_id(booking_id):
    """
    GET /api/bookings/:id
    Get booking by ID
    """
    return controller.get_booking_by_id(booking_id)

@booking_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_bookings(user_id):
    """
    GET /api/bookings/user/:user_id
    Get all bookings by user
    """
    return controller.get_user_bookings(user_id)

@booking_bp.route('/<int:booking_id>', methods=['PATCH'])
@token_required
def update_booking_status(booking_id):
    """
    PATCH /api/bookings/:id
    Update booking status (checkin, checkout, cancel)"""
    return controller.update_booking_status(booking_id)
