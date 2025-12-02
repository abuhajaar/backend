from src.models.floor import Floor
from src.config.database import db

class FloorRepository:
    """Repository for Floor operations"""
    
    @staticmethod
    def get_all():
        """Get all floors"""
        return Floor.query.all()
    
    @staticmethod
    def get_by_id(floor_id):
        """Get floor by ID"""
        return Floor.query.filter_by(id=floor_id).first()
    
    @staticmethod
    def get_by_name(name):
        """Get floor by name"""
        return Floor.query.filter_by(name=name).first()
    
    @staticmethod
    def create(name):
        """Create new floor"""
        floor = Floor(name=name)
        db.session.add(floor)
        db.session.commit()
        db.session.refresh(floor)
        return floor
    
    @staticmethod
    def update(floor_id, name=None):
        """Update floor"""
        floor = Floor.query.filter_by(id=floor_id).first()
        
        if not floor:
            return None
        
        if name is not None:
            floor.name = name
        
        db.session.commit()
        db.session.refresh(floor)
        return floor
    
    @staticmethod
    def delete(floor_id):
        """Delete floor"""
        floor = Floor.query.filter_by(id=floor_id).first()
        
        if not floor:
            return False
        
        db.session.delete(floor)
        db.session.commit()
        return True
