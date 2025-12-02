from typing import Dict
from datetime import datetime
from src.repositories.blackout_repository import BlackoutRepository
from src.repositories.user_repository import UserRepository
from src.config.database import db

class BlackoutUseCase:
    """UseCase for business logic Blackout"""
    
    def __init__(self):
        self.blackout_repository = BlackoutRepository()
        self.user_repository = UserRepository()
    
    def get_all_blackouts(self) -> Dict:
        """Get all blackouts with creator info"""
        try:
            blackouts = self.blackout_repository.get_all()
            blackouts_list = []
            
            for blackout in blackouts:
                blackout_data = blackout.to_dict()
                
                # Get creator info
                creator = self.user_repository.get_by_id(blackout.created_by)
                if creator:
                    blackout_data['created_by_name'] = creator.username
                    blackout_data['created_by_email'] = creator.email
                else:
                    blackout_data['created_by_name'] = None
                    blackout_data['created_by_email'] = None
                
                blackouts_list.append(blackout_data)
            
            return {
                'success': True,
                'data': blackouts_list,
                'count': len(blackouts_list)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_blackout_by_id(self, blackout_id: int) -> Dict:
        """Get blackout by ID"""
        try:
            blackout = self.blackout_repository.get_by_id(blackout_id)
            if blackout:
                blackout_data = blackout.to_dict()
                
                # Get creator info
                creator = self.user_repository.get_by_id(blackout.created_by)
                if creator:
                    blackout_data['created_by_name'] = creator.username
                    blackout_data['created_by_email'] = creator.email
                else:
                    blackout_data['created_by_name'] = None
                    blackout_data['created_by_email'] = None
                
                return {
                    'success': True,
                    'data': blackout_data
                }
            return {
                'success': False,
                'error': 'Blackout not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_blackout(self, title: str, start_at: str, end_at: str, created_by: int, description: str = None) -> Dict:
        """Create a new blackout"""
        try:
            # Validasi input
            if not title or not start_at or not end_at or not created_by:
                return {
                    'success': False,
                    'error': 'Title, start_at, end_at, and created_by are required'
                }
            
            # Parse datetime strings
            try:
                start_datetime = datetime.fromisoformat(start_at.replace('Z', '+00:00'))
                end_datetime = datetime.fromisoformat(end_at.replace('Z', '+00:00'))
            except ValueError:
                return {
                    'success': False,
                    'error': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }
            
            # Validasi end_at > start_at
            if end_datetime <= start_datetime:
                return {
                    'success': False,
                    'error': 'End time must be after start time'
                }
            
            # Validasi user exists
            creator = self.user_repository.get_by_id(created_by)
            if not creator:
                return {
                    'success': False,
                    'error': 'Creator user not found'
                }
            
            # Buat blackout baru
            new_blackout = self.blackout_repository.create(
                title=title,
                description=description,
                start_at=start_datetime,
                end_at=end_datetime,
                created_by=created_by
            )
            blackout_data = new_blackout.to_dict()
            blackout_data['created_by_name'] = creator.username
            blackout_data['created_by_email'] = creator.email
            
            return {
                'success': True,
                'data': blackout_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_blackout(self, blackout_id: int, title: str = None, description: str = None, start_at: str = None, end_at: str = None) -> Dict:
        """Update blackout"""
        try:
            # Parse datetime strings if provided
            start_datetime = None
            end_datetime = None
            
            if start_at:
                try:
                    start_datetime = datetime.fromisoformat(start_at.replace('Z', '+00:00'))
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid start_at datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                    }
            
            if end_at:
                try:
                    end_datetime = datetime.fromisoformat(end_at.replace('Z', '+00:00'))
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid end_at datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                    }
            
            # Validasi end_at > start_at if both provided
            if start_datetime and end_datetime and end_datetime <= start_datetime:
                return {
                    'success': False,
                    'error': 'End time must be after start time'
                }
            
            blackout = self.blackout_repository.update(
                blackout_id,
                title=title,
                description=description,
                start_at=start_datetime,
                end_at=end_datetime
            )
            
            if blackout:
                blackout_data = blackout.to_dict()
                
                # Get creator info
                creator = self.user_repository.get_by_id(blackout.created_by)
                if creator:
                    blackout_data['created_by_name'] = creator.username
                    blackout_data['created_by_email'] = creator.email
                else:
                    blackout_data['created_by_name'] = None
                    blackout_data['created_by_email'] = None
                
                return {
                    'success': True,
                    'data': blackout_data
                }
            return {
                'success': False,
                'error': 'Blackout not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_blackout(self, blackout_id: int) -> Dict:
        """Delete blackout"""
        try:
            success = self.blackout_repository.delete(blackout_id)
            if success:
                return {
                    'success': True,
                    'message': 'Blackout deleted successfully'
                }
            return {
                'success': False,
                'error': 'Blackout not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
