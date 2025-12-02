from typing import Dict
from src.repositories.amenity_repository import AmenityRepository
from src.repositories.space_repository import SpaceRepository
from src.config.database import db

class AmenityUseCase:
    """UseCase for business logic Amenity"""
    
    def __init__(self):
        self.amenity_repository = AmenityRepository()
        self.space_repository = SpaceRepository()
    
    def get_all_amenities(self) -> Dict:
        """Get all amenities with space name"""
        try:
            amenities = self.amenity_repository.get_all()
            amenities_list = []
            
            for amenity in amenities:
                amenity_data = amenity.to_dict()
                
                # Get space name
                space = self.space_repository.get_space_by_id(amenity.space_id)
                amenity_data['space_name'] = space.name if space else None
                
                amenities_list.append(amenity_data)
            
            return {
                'success': True,
                'data': amenities_list,
                'count': len(amenities_list)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_amenity_by_id(self, amenity_id: int) -> Dict:
        """Get amenity by ID"""
        try:
            amenity = self.amenity_repository.get_by_id(amenity_id)
            if amenity:
                amenity_data = amenity.to_dict()
                
                # Get space name
                space = self.space_repository.get_space_by_id(amenity.space_id)
                amenity_data['space_name'] = space.name if space else None
                
                return {
                    'success': True,
                    'data': amenity_data
                }
            return {
                'success': False,
                'error': 'Amenity not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_amenity(self, space_id: int, name: str, icon: str = None) -> Dict:
        """Create a new amenity"""
        try:
            # Validasi input
            if not space_id or not name:
                return {
                    'success': False,
                    'error': 'Space ID and name are required'
                }
            
            # Validasi space exists
            space = self.space_repository.get_space_by_id(space_id)
            if not space:
                return {
                    'success': False,
                    'error': 'Space not found'
                }
            
            # Buat amenity baru
            new_amenity = self.amenity_repository.create(
                space_id=space_id,
                name=name,
                icon=icon
            )
            amenity_data = new_amenity.to_dict()
            amenity_data['space_name'] = space.name
            
            return {
                'success': True,
                'data': amenity_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_amenity(self, amenity_id: int, space_id: int = None, name: str = None, icon: str = None) -> Dict:
        """Update amenity"""
        try:
            # Validasi space_id jika ada
            if space_id:
                space = self.space_repository.get_space_by_id(space_id)
                if not space:
                    return {
                        'success': False,
                        'error': 'Space not found'
                    }
            
            amenity = self.amenity_repository.update(
                amenity_id,
                space_id=space_id,
                name=name,
                icon=icon
            )
            
            if amenity:
                amenity_data = amenity.to_dict()
                
                # Get space name
                space = self.space_repository.get_space_by_id(amenity.space_id)
                amenity_data['space_name'] = space.name if space else None
                
                return {
                    'success': True,
                    'data': amenity_data
                }
            return {
                'success': False,
                'error': 'Amenity not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_amenity(self, amenity_id: int) -> Dict:
        """Delete amenity"""
        try:
            success = self.amenity_repository.delete(amenity_id)
            if success:
                return {
                    'success': True,
                    'message': 'Amenity deleted successfully'
                }
            return {
                'success': False,
                'error': 'Amenity not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
