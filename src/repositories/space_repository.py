"""
Repository untuk Space
Menghandle data access layer untuk Space
"""
from src.models.space import Space
from src.models.floor import Floor
from src.models.amenity import Amenity
from src.config.database import db

class SpaceRepository:
    """Repository untuk operasi database Space"""
    
    @staticmethod
    def get_all_spaces():
        """
        Get all spaces dengan floor dan amenities
        Returns: List of Space objects
        """
        return Space.query.all()
    
    @staticmethod
    def get_space_by_id(space_id):
        """
        Get space by ID
        Args:
            space_id: ID of the space
        Returns: Space object or None
        """
        return Space.query.filter_by(id=space_id).first()
