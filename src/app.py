from flask import Flask
from flask_cors import CORS
from src.config.config import Config
from src.config.database import db
from src.routes.user_routes import user_routes
from src.routes.health_routes import health_routes
from src.routes.auth_routes import auth_routes
from src.routes.space_routes import space_routes
from src.routes.booking_routes import booking_bp
from src.routes.stats_routes import stats_bp
from src.routes.department_routes import department_routes
from src.routes.floor_routes import floor_routes
from src.routes.amenity_routes import amenity_routes
from src.routes.blackout_routes import blackout_routes
from src.routes.announcement_routes import announcement_routes
from src.routes.assignment_routes import assignment_routes
from src.routes.task_routes import task_routes
from src.utils.error_handlers import register_error_handlers
from src.config.socketio import init_socketio
from src.websocket.announcement_socket import AnnouncementNamespace

# Import all models so SQLAlchemy creates the tables
from src.models.user import User
from src.models.department import Department
from src.models.floor import Floor
from src.models.space import Space
from src.models.amenity import Amenity
from src.models.blackout import Blackout
from src.models.booking import Booking
from src.models.announcement import Announcement
from src.models.assignment import Assignment
from src.models.task import Task

def create_app():
    """Application factory untuk membuat Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Initialize SocketIO
    socketio = init_socketio(app)
    
    # Register WebSocket namespaces
    socketio.on_namespace(AnnouncementNamespace('/announcements'))
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(health_routes, url_prefix='/api')
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(user_routes, url_prefix='/api/users')
    app.register_blueprint(department_routes, url_prefix='/api/departments')
    app.register_blueprint(floor_routes, url_prefix='/api/floors')
    app.register_blueprint(amenity_routes, url_prefix='/api/amenities')
    app.register_blueprint(blackout_routes, url_prefix='/api/blackouts')
    app.register_blueprint(announcement_routes, url_prefix='/api/announcements')
    app.register_blueprint(assignment_routes, url_prefix='/api/assignments')
    app.register_blueprint(task_routes, url_prefix='/api/tasks')
    app.register_blueprint(space_routes, url_prefix='/api/spaces')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app, socketio
