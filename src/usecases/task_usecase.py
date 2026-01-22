from typing import Dict
from src.repositories.task_repository import TaskRepository
from src.repositories.assignment_repository import AssignmentRepository
from src.repositories.user_repository import UserRepository

class TaskUseCase:
    """UseCase for Task business logic"""
    
    def __init__(self):
        self.task_repository = TaskRepository()
        self.assignment_repository = AssignmentRepository()
        self.user_repository = UserRepository()
    
    def get_tasks_by_assignment(self, assignment_id: int, manager_department_id: int) -> Dict:
        """Get all tasks for specific assignment (manager can only access tasks from their department)"""
        try:
            # Validate assignment exists
            assignment = self.assignment_repository.get_by_id(assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}
            
            # Manager can only access assignments from their department
            if assignment.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only access assignments from your department'}
            
            # Get all tasks for this assignment
            tasks = self.task_repository.get_by_assignment(assignment_id)
            
            # Sort by priority (high -> medium -> low) then by created_at
            priority_order = {'high': 1, 'medium': 2, 'low': 3}
            tasks.sort(key=lambda x: (priority_order.get(x.priority, 4), x.created_at))
            
            # Build response with assigned user info
            tasks_list = []
            for task in tasks:
                # Get assigned user info
                assigned_user = self.user_repository.get_by_id(task.user_id)
                assigned_user_name = assigned_user.username if assigned_user else "Unknown"
                
                task_data = {
                    'id': task.id,
                    'title': task.title,
                    'priority': task.priority,
                    'assignment_id': task.assignment_id,
                    'user_id': task.user_id,
                    'user_name': assigned_user_name,
                    'is_done': task.is_done,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None
                }
                
                tasks_list.append(task_data)
            
            return {
                'success': True,
                'data': {
                    'assignment_id': assignment_id,
                    'assignment_title': assignment.title,
                    'tasks': tasks_list,
                    'total_tasks': len(tasks_list),
                    'completed_tasks': len([t for t in tasks if t.is_done])
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_task(self, assignment_id: int, title: str, priority: str, 
                   user_id: int, is_done: bool, manager_department_id: int) -> Dict:
        """Create new task with validations"""
        try:
            # Validate assignment exists
            assignment = self.assignment_repository.get_by_id(assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}
            
            # Manager can only create tasks for assignments in their department
            if assignment.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only create tasks for assignments in your department'}
            
            # Validate required fields
            if not title or not title.strip():
                return {'success': False, 'error': 'Title is required'}
            
            if not priority:
                priority = 'medium'  # Default priority
            
            # Validate priority value
            if priority not in ['low', 'medium', 'high']:
                return {'success': False, 'error': 'Priority must be low, medium, or high'}
            
            if not user_id:
                return {'success': False, 'error': 'User ID is required'}
            
            # Validate user exists and is in the same department
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            if user.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only assign tasks to users in your department'}
            
            # Create task
            task_data = {
                'title': title.strip(),
                'priority': priority,
                'assignment_id': assignment_id,
                'user_id': user_id,
                'is_done': is_done if is_done is not None else False
            }
            
            task = self.task_repository.create(task_data)
            
            # Get user info for response
            user_name = user.username
            
            return {
                'success': True,
                'data': {
                    'id': task.id,
                    'title': task.title,
                    'priority': task.priority,
                    'assignment_id': task.assignment_id,
                    'user_id': task.user_id,
                    'user_name': user_name,
                    'is_done': task.is_done,
                    'created_at': task.created_at.isoformat() if task.created_at else None
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_task(self, task_id: int, title: str, priority: str, 
                   user_id_to_assign: int, is_done: bool, current_user_id: int,
                   current_user_department_id: int, current_user_role: str) -> Dict:
        """Update task with validations (manager can update all fields, employee can only update is_done)"""
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Get assignment to validate department
            assignment = self.assignment_repository.get_by_id(task.assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}
            
            # Role-based authorization
            if current_user_role == 'employee':
                # Employee can only update their own tasks and only the is_done field
                if task.user_id != current_user_id:
                    return {'success': False, 'error': 'You can only update tasks assigned to you'}
                
                # Employee can only update is_done field
                if title is not None or priority is not None or user_id_to_assign is not None:
                    return {'success': False, 'error': 'Employees can only update task completion status (is_done)'}
                
                update_data = {}
                if is_done is not None:
                    update_data['is_done'] = is_done
                    
            elif current_user_role == 'manager':
                # Manager can only update tasks from their department
                if assignment.department_id != current_user_department_id:
                    return {'success': False, 'error': 'You can only update tasks from your department'}
                
                # Build update data - manager can update all fields
                update_data = {}
                
                if title is not None:
                    if not title.strip():
                        return {'success': False, 'error': 'Title cannot be empty'}
                    update_data['title'] = title.strip()
                
                if priority is not None:
                    if priority not in ['low', 'medium', 'high']:
                        return {'success': False, 'error': 'Priority must be low, medium, or high'}
                    update_data['priority'] = priority
                
                if user_id_to_assign is not None:
                    # Validate user exists and is in the same department
                    user = self.user_repository.get_by_id(user_id_to_assign)
                    if not user:
                        return {'success': False, 'error': 'User not found'}
                    
                    if user.department_id != current_user_department_id:
                        return {'success': False, 'error': 'You can only assign tasks to users in your department'}
                    
                    update_data['user_id'] = user_id_to_assign
                
                if is_done is not None:
                    update_data['is_done'] = is_done
            else:
                # Superadmin or other roles
                return {'success': False, 'error': 'Unauthorized to update tasks'}
            
            # Update task
            updated_task = self.task_repository.update(task_id, update_data)
            
            # Get user info for response
            user = self.user_repository.get_by_id(updated_task.user_id)
            user_name = user.username if user else 'Unknown'
            
            return {
                'success': True,
                'data': {
                    'id': updated_task.id,
                    'title': updated_task.title,
                    'priority': updated_task.priority,
                    'assignment_id': updated_task.assignment_id,
                    'user_id': updated_task.user_id,
                    'user_name': user_name,
                    'is_done': updated_task.is_done,
                    'created_at': updated_task.created_at.isoformat() if updated_task.created_at else None,
                    'updated_at': updated_task.updated_at.isoformat() if updated_task.updated_at else None
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_task(self, task_id: int, manager_department_id: int) -> Dict:
        """Delete task with validation - only from manager's department"""
        try:
            # Get existing task
            task = self.task_repository.get_by_id(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Get assignment to validate department
            assignment = self.assignment_repository.get_by_id(task.assignment_id)
            if not assignment:
                return {'success': False, 'error': 'Assignment not found'}
            
            # Manager can only delete tasks from their department
            if assignment.department_id != manager_department_id:
                return {'success': False, 'error': 'You can only delete tasks from your department'}
            
            # Delete task (incomplete tasks are allowed to be deleted)
            deleted = self.task_repository.delete(task_id)
            
            if deleted:
                return {'success': True}
            else:
                return {'success': False, 'error': 'Failed to delete task'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
