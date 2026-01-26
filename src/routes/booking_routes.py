from flask import Blueprint
from src.controllers.booking_controller import BookingController
from src.utils.jwt_helper import token_required, role_required

# Create blueprint
booking_bp = Blueprint('booking', __name__)

# Initialize controller
controller = BookingController()

# User endpoints
@booking_bp.route('', methods=['GET', 'POST'])
@token_required
def handle_bookings():
    """
    GET /api/bookings - Get current user's bookings
    POST /api/bookings - Create new booking
    """
    from flask import request
    if request.method == 'GET':
        # Get current user from token
        user = request.current_user
        return controller.get_user_bookings(user['user_id'])
    else:  # POST
        return controller.create_booking()

@booking_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_bookings(user_id):
    """
    GET /api/bookings/user/:user_id
    Get all bookings by user
    """
    return controller.get_user_bookings(user_id)

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@token_required
def get_booking_by_id(booking_id):
    """
    GET /api/bookings/:id
    Get booking by ID
    """
    return controller.get_booking_by_id(booking_id)

@booking_bp.route('/<int:booking_id>', methods=['PATCH'])
@token_required
def update_booking_status(booking_id):
    """
    PATCH /api/bookings/:id
    Update booking status (checkin, checkout, cancel)
    """
    return controller.update_booking_status(booking_id)



###############################################################################


# Management endpoints (superadmin only) - Read and Delete Only
@booking_bp.route('/manage', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_bookings_for_management():
    """
    GET /api/bookings/manage
    Get all bookings for management (superadmin only)
    """
    return controller.get_bookings_for_management()

@booking_bp.route('/manage/<int:booking_id>', methods=['GET'])
@token_required
@role_required(['superadmin'])
def get_booking_for_management(booking_id):
    """
    GET /api/bookings/manage/:id
    Get booking by ID for management (superadmin only)
    """
    return controller.get_booking_for_management(booking_id)

@booking_bp.route('/manage/<int:booking_id>', methods=['DELETE'])
@token_required
@role_required(['superadmin'])
def delete_booking(booking_id):
    """
    DELETE /api/bookings/manage/:id
    Delete booking (superadmin only)
    """
    return controller.delete_booking(booking_id)

