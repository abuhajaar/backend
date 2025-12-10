from typing import Dict
from src.repositories.announcement_repository import AnnouncementRepository
from src.repositories.user_repository import UserRepository
from src.repositories.department_repository import DepartmentRepository

class AnnouncementUseCase:
    """UseCase for Announcement business logic"""
    
    def __init__(self):
        self.announcement_repository = AnnouncementRepository()
        self.user_repository = UserRepository()
        self.department_repository = DepartmentRepository()
    
    def get_announcements_for_manager(self, manager_department_id: int) -> Dict:
        """Get announcements for manager (company-wide + department-specific)"""
        try:
            if not manager_department_id:
                return {
                    'success': False,
                    'error': 'Manager tidak memiliki department'
                }
            
            # Get company-wide announcements (department_id is NULL)
            company_wide = self.announcement_repository.get_company_wide()
            
            # Get department-specific announcements
            department_specific = self.announcement_repository.get_by_department(manager_department_id)
            
            # Combine both lists
            all_announcements = company_wide + department_specific
            
            # Sort by created_at descending (newest first)
            all_announcements.sort(key=lambda x: x.created_at, reverse=True)
            
            # Build response with creator and department info
            announcements_list = []
            for announcement in all_announcements:
                # Get creator info
                creator = self.user_repository.get_by_id(announcement.created_by)
                creator_name = creator.username if creator else "Unknown"
                
                # Get department info
                department_name = None
                if announcement.department_id:
                    department = self.department_repository.get_by_id(announcement.department_id)
                    department_name = department.name if department else None
                
                announcement_data = {
                    'id': announcement.id,
                    'title': announcement.title,
                    'description': announcement.description,
                    'creator_id': announcement.created_by,
                    'creator_name': creator_name,
                    'department_id': announcement.department_id,
                    'department_name': department_name,
                    'created_at': announcement.created_at.isoformat() if announcement.created_at else None
                }
                
                announcements_list.append(announcement_data)
            
            return {
                'success': True,
                'data': announcements_list
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_announcement(self, title: str, description: str, created_by: int, 
                          department_id: int, manager_id: int, manager_department_id: int) -> Dict:
        """Create new announcement with validations"""
        try:
            # Validate required fields
            if not title or not title.strip():
                return {'success': False, 'error': 'Title is required'}
            
            if not description or not description.strip():
                return {'success': False, 'error': 'Description is required'}
            
            # created_by is automatically assigned from manager_id (JWT token)
            # Validate creator exists
            creator = self.user_repository.get_by_id(created_by)
            if not creator:
                return {'success': False, 'error': 'Creator user not found'}
            
            # Validate department_id if provided (None means company-wide)
            if department_id is not None:
                department = self.department_repository.get_by_id(department_id)
                if not department:
                    return {'success': False, 'error': 'Department not found'}
                
                # Manager can only create announcement for their own department or company-wide
                if department_id != manager_department_id:
                    return {'success': False, 'error': 'You can only create announcements for your own department or company-wide'}
            
            # Create announcement
            announcement_data = {
                'title': title.strip(),
                'description': description.strip(),
                'created_by': created_by,
                'department_id': department_id
            }
            
            announcement = self.announcement_repository.create(announcement_data)
            
            # Get creator and department info for response
            creator_name = creator.username
            department_name = None
            if department_id:
                department = self.department_repository.get_by_id(department_id)
                department_name = department.name if department else None
            
            return {
                'success': True,
                'data': {
                    'id': announcement.id,
                    'title': announcement.title,
                    'description': announcement.description,
                    'creator_id': announcement.created_by,
                    'creator_name': creator_name,
                    'department_id': announcement.department_id,
                    'department_name': department_name,
                    'created_at': announcement.created_at.isoformat() if announcement.created_at else None
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_announcement(self, announcement_id: int, title: str, description: str, 
                          department_id: int, manager_id: int, 
                          manager_department_id: int) -> Dict:
        """Update announcement with validations"""
        try:
            # Get existing announcement
            announcement = self.announcement_repository.get_by_id(announcement_id)
            if not announcement:
                return {'success': False, 'error': 'Announcement not found'}
            
            # Manager can only update announcements they created or from their department
            if announcement.created_by != manager_id and announcement.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only update announcements you created or from your department'}
            
            # Build update data (created_by cannot be changed)
            update_data = {}
            
            if title is not None:
                if not title.strip():
                    return {'success': False, 'error': 'Title cannot be empty'}
                update_data['title'] = title.strip()
            
            if description is not None:
                if not description.strip():
                    return {'success': False, 'error': 'Description cannot be empty'}
                update_data['description'] = description.strip()
            
            # Handle department_id update (can be set to null for company-wide)
            if department_id != 'NOT_PROVIDED':
                if department_id is not None:
                    # Validate department exists
                    department = self.department_repository.get_by_id(department_id)
                    if not department:
                        return {'success': False, 'error': 'Department not found'}
                    
                    # Manager can only set to their own department
                    if department_id != manager_department_id:
                        return {'success': False, 'error': 'You can only set department to your own department or company-wide'}
                
                # Allow setting to null (company-wide)
                update_data['department_id'] = department_id
            
            # Update announcement
            updated_announcement = self.announcement_repository.update(announcement_id, update_data)
            
            # Get creator and department info for response
            creator = self.user_repository.get_by_id(updated_announcement.created_by)
            creator_name = creator.username if creator else 'Unknown'
            
            department_name = None
            if updated_announcement.department_id:
                department = self.department_repository.get_by_id(updated_announcement.department_id)
                department_name = department.name if department else None
            
            return {
                'success': True,
                'data': {
                    'id': updated_announcement.id,
                    'title': updated_announcement.title,
                    'description': updated_announcement.description,
                    'creator_id': updated_announcement.created_by,
                    'creator_name': creator_name,
                    'department_id': updated_announcement.department_id,
                    'department_name': department_name,
                    'created_at': updated_announcement.created_at.isoformat() if updated_announcement.created_at else None,
                    'updated_at': updated_announcement.updated_at.isoformat() if updated_announcement.updated_at else None
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_announcement(self, announcement_id: int, manager_id: int, 
                          manager_department_id: int) -> Dict:
        """Delete announcement with validation - only from manager's department"""
        try:
            # Get existing announcement
            announcement = self.announcement_repository.get_by_id(announcement_id)
            if not announcement:
                return {'success': False, 'error': 'Announcement not found'}
            
            # Manager can only delete announcements from their department
            if announcement.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only delete announcements from your department'}
            
            # Delete announcement
            deleted = self.announcement_repository.delete(announcement_id)
            
            if deleted:
                return {'success': True}
            else:
                return {'success': False, 'error': 'Failed to delete announcement'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
