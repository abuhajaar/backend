from typing import List, Optional
from src.models.announcement import Announcement
from src.config.database import db

class AnnouncementRepository:
    """Repository for Announcement operations"""
    
    def get_all(self) -> List[Announcement]:
        """Get all announcements"""
        return Announcement.query.order_by(Announcement.created_at.desc()).all()
    
    def get_by_id(self, announcement_id: int) -> Optional[Announcement]:
        """Get announcement by ID"""
        return Announcement.query.get(announcement_id)
    
    def get_company_wide(self) -> List[Announcement]:
        """Get company-wide announcements (department_id is NULL)"""
        return Announcement.query.filter(Announcement.department_id.is_(None)).all()
    
    def get_by_department(self, department_id: int) -> List[Announcement]:
        """Get announcements for specific department"""
        return Announcement.query.filter_by(department_id=department_id).all()
    
    def create(self, announcement_data: dict) -> Announcement:
        """Create new announcement"""
        announcement = Announcement(
            title=announcement_data.get('title'),
            description=announcement_data.get('description'),
            created_by=announcement_data.get('created_by'),
            department_id=announcement_data.get('department_id')
        )
        db.session.add(announcement)
        db.session.commit()
        db.session.refresh(announcement)
        return announcement
    
    def update(self, announcement_id: int, update_data: dict) -> Optional[Announcement]:
        """Update announcement"""
        announcement = self.get_by_id(announcement_id)
        if announcement:
            if 'title' in update_data:
                announcement.title = update_data['title']
            if 'description' in update_data:
                announcement.description = update_data['description']
            if 'department_id' in update_data:
                announcement.department_id = update_data['department_id']
            db.session.commit()
            db.session.refresh(announcement)
        return announcement
    
    def delete(self, announcement_id: int) -> bool:
        """Delete announcement"""
        announcement = self.get_by_id(announcement_id)
        if announcement:
            db.session.delete(announcement)
            db.session.commit()
            return True
        return False
