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
    def get_by_id(space_id):
        """Get space by ID"""
        return Space.query.filter_by(id=space_id).first()
    
    @staticmethod
    def get_space_by_id(space_id):
        """Get space by ID (alias for backward compatibility)"""
        return SpaceRepository.get_by_id(space_id)
    
    @staticmethod
    def get_by_name(name):
        """Get space by name"""
        return Space.query.filter_by(name=name).first()
    
    @staticmethod
    def count_by_floor_id(floor_id):
        """Count total spaces on a specific floor"""
        return Space.query.filter_by(location=floor_id).count()
    
    @staticmethod
    def create(name, type, capacity, location, opening_hours=None, max_duration=None, status='available'):
        """Create new space"""
        space = Space(
            name=name,
            type=type,
            capacity=capacity,
            location=location,
            opening_hours=opening_hours,
            max_duration=max_duration,
            status=status
        )
        db.session.add(space)
        db.session.commit()
        db.session.refresh(space)
        return space
    
    @staticmethod
    def update(space_id, name=None, type=None, capacity=None, location=None, opening_hours=None, max_duration=None, status=None):
        """Update space"""
        space = Space.query.filter_by(id=space_id).first()
        
        if not space:
            return None
        
        if name is not None:
            space.name = name
        if type is not None:
            space.type = type
        if capacity is not None:
            space.capacity = capacity
        if location is not None:
            space.location = location
        if opening_hours is not None:
            space.opening_hours = opening_hours
        if max_duration is not None:
            space.max_duration = max_duration
        if status is not None:
            space.status = status
        
        db.session.commit()
        db.session.refresh(space)
        return space
    
    @staticmethod
    def delete(space_id):
        """Delete space"""
        space = Space.query.filter_by(id=space_id).first()
        
        if not space:
            return False
        
        db.session.delete(space)
        db.session.commit()
        return True
    
    @staticmethod
    def get_floor_by_id(floor_id):
        """Get floor by ID"""
        from src.models.floor import Floor
        return Floor.query.filter_by(id=floor_id).first()
