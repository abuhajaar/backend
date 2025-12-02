from src.models.blackout import Blackout
from src.config.database import db
from datetime import datetime

class BlackoutRepository:
    """Repository for Blackout operations"""
    
    @staticmethod
    def get_all():
        """Get all blackouts"""
        return Blackout.query.order_by(Blackout.start_at.desc()).all()
    
    @staticmethod
    def get_by_id(blackout_id):
        """Get blackout by ID"""
        return Blackout.query.filter_by(id=blackout_id).first()
    
    @staticmethod
    def get_active_blackouts(target_date=None):
        """Get blackouts that are currently active or for a specific date"""
        if target_date is None:
            target_date = datetime.utcnow()
        
        return Blackout.query.filter(
            Blackout.start_at <= target_date,
            Blackout.end_at >= target_date
        ).all()
    
    @staticmethod
    def create(title, start_at, end_at, created_by, description=None):
        """Create new blackout"""
        blackout = Blackout(
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            created_by=created_by
        )
        db.session.add(blackout)
        db.session.commit()
        db.session.refresh(blackout)
        return blackout
    
    @staticmethod
    def update(blackout_id, title=None, description=None, start_at=None, end_at=None):
        """Update blackout"""
        blackout = Blackout.query.filter_by(id=blackout_id).first()
        
        if not blackout:
            return None
        
        if title is not None:
            blackout.title = title
        if description is not None:
            blackout.description = description
        if start_at is not None:
            blackout.start_at = start_at
        if end_at is not None:
            blackout.end_at = end_at
        
        db.session.commit()
        db.session.refresh(blackout)
        return blackout
    
    @staticmethod
    def delete(blackout_id):
        """Delete blackout"""
        blackout = Blackout.query.filter_by(id=blackout_id).first()
        
        if not blackout:
            return False
        
        db.session.delete(blackout)
        db.session.commit()
        return True
