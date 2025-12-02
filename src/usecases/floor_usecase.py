from typing import Dict
from src.repositories.floor_repository import FloorRepository
from src.repositories.space_repository import SpaceRepository
from src.config.database import db

class FloorUseCase:
    """UseCase for business logic Floor"""
    
    def __init__(self):
        self.floor_repository = FloorRepository()
        self.space_repository = SpaceRepository()
    
    def get_all_floors(self) -> Dict:
        """Get all floors with total spaces count"""
        try:
            floors = self.floor_repository.get_all()
            floors_list = []
            
            for floor in floors:
                floor_data = floor.to_dict()
                
                # Count total spaces on this floor
                total_spaces = self.space_repository.count_by_floor_id(floor.id)
                floor_data['total_spaces'] = total_spaces
                
                floors_list.append(floor_data)
            
            return {
                'success': True,
                'data': floors_list,
                'count': len(floors_list)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_floor_by_id(self, floor_id: int) -> Dict:
        """Get floor by ID"""
        try:
            floor = self.floor_repository.get_by_id(floor_id)
            if floor:
                floor_data = floor.to_dict()
                
                # Count total spaces on this floor
                total_spaces = self.space_repository.count_by_floor_id(floor.id)
                floor_data['total_spaces'] = total_spaces
                
                return {
                    'success': True,
                    'data': floor_data
                }
            return {
                'success': False,
                'error': 'Floor not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_floor(self, name: str) -> Dict:
        """Create a new floor"""
        try:
            # Validasi input
            if not name:
                return {
                    'success': False,
                    'error': 'Name is required'
                }
            
            # Cek apakah nama floor sudah ada
            existing_floor = self.floor_repository.get_by_name(name)
            if existing_floor:
                return {
                    'success': False,
                    'error': 'Floor name already exists'
                }
            
            # Buat floor baru
            new_floor = self.floor_repository.create(name=name)
            floor_data = new_floor.to_dict()
            floor_data['total_spaces'] = 0
            
            return {
                'success': True,
                'data': floor_data
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_floor(self, floor_id: int, name: str = None) -> Dict:
        """Update floor"""
        try:
            # Cek apakah nama baru sudah digunakan floor lain
            if name:
                existing_floor = self.floor_repository.get_by_name(name)
                if existing_floor and existing_floor.id != floor_id:
                    return {
                        'success': False,
                        'error': 'Floor name already exists'
                    }
            
            floor = self.floor_repository.update(floor_id, name=name)
            if floor:
                floor_data = floor.to_dict()
                
                # Count total spaces on this floor
                total_spaces = self.space_repository.count_by_floor_id(floor.id)
                floor_data['total_spaces'] = total_spaces
                
                return {
                    'success': True,
                    'data': floor_data
                }
            return {
                'success': False,
                'error': 'Floor not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_floor(self, floor_id: int) -> Dict:
        """Delete floor"""
        try:
            # Cek apakah masih ada spaces di floor ini
            total_spaces = self.space_repository.count_by_floor_id(floor_id)
            if total_spaces > 0:
                return {
                    'success': False,
                    'error': f'Cannot delete floor. Still has {total_spaces} spaces assigned.'
                }
            
            success = self.floor_repository.delete(floor_id)
            if success:
                return {
                    'success': True,
                    'message': 'Floor deleted successfully'
                }
            return {
                'success': False,
                'error': 'Floor not found'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
