from typing import Dict
from datetime import datetime
from src.repositories.assignment_repository import AssignmentRepository
from src.repositories.user_repository import UserRepository
from src.repositories.department_repository import DepartmentRepository

class AssignmentUseCase:
    """UseCase for Assignment business logic"""
    
    def __init__(self):
        self.assignment_repository = AssignmentRepository()
        self.user_repository = UserRepository()
        self.department_repository = DepartmentRepository()
    
    def get_assignments_for_department(self, department_id: int) -> Dict:
        """Get all assignments for specific department"""
        try:
            if not department_id:
                return {
                    'success': False,
                    'error': 'Manager does not have a department'
                }
            
            # Get all assignments for the department
            assignments = self.assignment_repository.get_by_department(department_id)
            
            # Sort by due_date ascending (earliest first)
            assignments.sort(key=lambda x: x.due_date if x.due_date else datetime.max)
            
            # Build response with creator and department info
            assignments_list = []
            for assignment in assignments:
                # Get creator info
                creator = self.user_repository.get_by_id(assignment.created_by)
                creator_name = creator.username if creator else "Unknown"
                
                # Get department info
                department = self.department_repository.get_by_id(assignment.department_id)
                department_name = department.name if department else "Unknown"
                
                # Get task count
                task_count = len(assignment.tasks) if assignment.tasks else 0
                task_done = len([task for task in assignment.tasks if task.is_done]) if assignment.tasks else 0
                
                assignment_data = {
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'creator_id': assignment.created_by,
                    'creator_name': creator_name,
                    'department_id': assignment.department_id,
                    'department_name': department_name,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'task_count': task_count,
                    'task_done': task_done,
                    'created_at': assignment.created_at.isoformat() if assignment.created_at else None
                }
                
                assignments_list.append(assignment_data)
            
            return {
                'success': True,
                'data': assignments_list
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_assignment(self, title: str, description: str, due_date: str, 
                         created_by: int, department_id: int) -> Dict:
        """Create new assignment with validations"""
        try:
            # Validate required fields
            if not title or not title.strip():
                return {'success': False, 'error': 'Title is required'}
            
            if not description or not description.strip():
                return {'success': False, 'error': 'Description is required'}
            
            if not due_date:
                return {'success': False, 'error': 'Due date is required'}
            
            # Parse due_date
            try:
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return {'success': False, 'error': 'Invalid due date format. Use ISO format (e.g., 2025-12-20T17:00:00)'}
            
            # Validate department
            if not department_id:
                return {'success': False, 'error': 'Manager does not have a department'}
            
            department = self.department_repository.get_by_id(department_id)
            if not department:
                return {'success': False, 'error': 'Department not found'}
            
            # Validate creator
            creator = self.user_repository.get_by_id(created_by)
            if not creator:
                return {'success': False, 'error': 'Creator user not found'}
            
            # Create assignment
            assignment_data = {
                'title': title.strip(),
                'description': description.strip(),
                'created_by': created_by,
                'department_id': department_id,
                'due_date': due_date_obj
            }
            
            assignment = self.assignment_repository.create(assignment_data)
            
            # Get creator and department info for response
            creator_name = creator.username
            department_name = department.name
            
            return {
                'success': True,
                'data': {
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'creator_id': assignment.created_by,
                    'creator_name': creator_name,
                    'department_id': assignment.department_id,
                    'department_name': department_name,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'task_count': 0,
                    'task_done': 0,
                    'created_at': assignment.created_at.isoformat() if assignment.created_at else None
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_assignment(self, assignment_id: int, title: str, description: str, 
                         due_date: str, manager_id: int, manager_department_id: int) -> Dict:
        """Update assignment with validations"""
        try:
            # Get existing assignment
            assignment = self.assignment_repository.get_by_id(assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}
            
            # Manager can only update assignments from their department
            if assignment.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only update assignments from your department'}
            
            # Build update data (created_by and department_id cannot be changed)
            update_data = {}
            
            if title is not None:
                if not title.strip():
                    return {'success': False, 'error': 'Title cannot be empty'}
                update_data['title'] = title.strip()
            
            if description is not None:
                if not description.strip():
                    return {'success': False, 'error': 'Description cannot be empty'}
                update_data['description'] = description.strip()
            
            if due_date is not None:
                # Parse due_date
                try:
                    due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    update_data['due_date'] = due_date_obj
                except (ValueError, AttributeError):
                    return {'success': False, 'error': 'Invalid due date format. Use ISO format (e.g., 2025-12-20T17:00:00)'}
            
            # Update assignment
            updated_assignment = self.assignment_repository.update(assignment_id, update_data)
            
            # Get creator and department info for response
            creator = self.user_repository.get_by_id(updated_assignment.created_by)
            creator_name = creator.username if creator else 'Unknown'
            
            department = self.department_repository.get_by_id(updated_assignment.department_id)
            department_name = department.name if department else 'Unknown'
            
            task_count = len(updated_assignment.tasks) if updated_assignment.tasks else 0
            task_done = len([task for task in updated_assignment.tasks if task.is_done]) if updated_assignment.tasks else 0
            
            return {
                'success': True,
                'data': {
                    'id': updated_assignment.id,
                    'title': updated_assignment.title,
                    'description': updated_assignment.description,
                    'creator_id': updated_assignment.created_by,
                    'creator_name': creator_name,
                    'department_id': updated_assignment.department_id,
                    'department_name': department_name,
                    'due_date': updated_assignment.due_date.isoformat() if updated_assignment.due_date else None,
                    'task_count': task_count,
                    'task_done': task_done,
                    'created_at': updated_assignment.created_at.isoformat() if updated_assignment.created_at else None,
                    'updated_at': updated_assignment.updated_at.isoformat() if updated_assignment.updated_at else None
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_assignment(self, assignment_id: int, manager_id: int, 
                         manager_department_id: int) -> Dict:
        """Delete assignment with validation - only from manager's department and all tasks must be completed"""
        try:
            # Get existing assignment
            assignment = self.assignment_repository.get_by_id(assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}
            
            # Manager can only delete assignments from their department
            if assignment.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only delete assignments from your department'}
            
            # Check if all tasks are completed
            if assignment.tasks:
                incomplete_tasks = [task for task in assignment.tasks if not task.is_done]
                if incomplete_tasks:
                    incomplete_count = len(incomplete_tasks)
                    return {
                        'success': False, 
                        'error': f'Cannot delete assignment with {incomplete_count} incomplete task(s). All tasks must be completed first.'
                    }
            
            # Delete assignment (tasks will be cascade deleted)
            deleted = self.assignment_repository.delete(assignment_id)
            
            if deleted:
                return {'success': True}
            else:
                return {'success': False, 'error': 'Failed to delete assignment'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
