from src.models.amenity import Amenity
from src.config.database import db

class AmenityRepository:
    """Repository for Amenity operations"""
    
    @staticmethod
    def get_all():
        """Get all amenities"""
        return Amenity.query.all()
    
    @staticmethod
    def get_by_id(amenity_id):
        """Get amenity by ID"""
        return Amenity.query.filter_by(id=amenity_id).first()
    
    @staticmethod
    def get_by_space_id(space_id):
        """Get all amenities for a specific space"""
        return Amenity.query.filter_by(space_id=space_id).all()
    
    @staticmethod
    def create(space_id, name, icon=None):
        """Create new amenity"""
        amenity = Amenity(space_id=space_id, name=name, icon=icon)
        db.session.add(amenity)
        db.session.commit()
        db.session.refresh(amenity)
        return amenity
    
    @staticmethod
    def update(amenity_id, space_id=None, name=None, icon=None):
        """Update amenity"""
        amenity = Amenity.query.filter_by(id=amenity_id).first()
        
        if not amenity:
            return None
        
        if space_id is not None:
            amenity.space_id = space_id
        if name is not None:
            amenity.name = name
        if icon is not None:
            amenity.icon = icon
        
        db.session.commit()
        db.session.refresh(amenity)
        return amenity
    
    @staticmethod
    def delete(amenity_id):
        """Delete amenity"""
        amenity = Amenity.query.filter_by(id=amenity_id).first()
        
        if not amenity:
            return False
        
        db.session.delete(amenity)
        db.session.commit()
        return True
