from src.models.space import Space
from src.models.floor import Floor
from src.models.amenity import Amenity
from src.config.database import db

class SpaceRepository:
    """Repository for Space operations"""
    
    @staticmethod
    def get_all_spaces():
        """Get all spaces with their floors and amenities"""
        return Space.query.all()
    
    @staticmethod
    def get_space_by_id(space_id):
        """Get space by ID"""
        return Space.query.filter_by(id=space_id).first()
