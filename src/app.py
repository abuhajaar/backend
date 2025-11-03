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
from src.utils.error_handlers import register_error_handlers

# Import all models so SQLAlchemy creates the tables
from src.models.user import User
from src.models.department import Department
from src.models.floor import Floor
from src.models.space import Space
from src.models.amenity import Amenity
from src.models.blackout import Blackout
from src.models.booking import Booking

def create_app():
    """Application factory untuk membuat Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(health_routes, url_prefix='/api')
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(space_routes, url_prefix='/api')
    app.register_blueprint(booking_bp)  # booking_bp sudah punya url_prefix di definisi
    app.register_blueprint(stats_bp)  # stats_bp sudah punya url_prefix di definisi
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
