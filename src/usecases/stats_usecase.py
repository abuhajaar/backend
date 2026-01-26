from typing import Dict
from src.repositories.stats_repository import StatsRepository
from src.repositories.announcement_repository import AnnouncementRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.repositories.assignment_repository import AssignmentRepository
from src.repositories.department_repository import DepartmentRepository

class StatsUseCase:
    """UseCase for business logic Statistics"""
    
    def __init__(self):
        self.stats_repository = StatsRepository()
        self.announcement_repository = AnnouncementRepository()
        self.task_repository = TaskRepository()
        self.user_repository = UserRepository()
        self.assignment_repository = AssignmentRepository()
        self.department_repository = DepartmentRepository()
    
    def get_user_stats(self, user_id: int, department_id: int, role: str = 'employee') -> Dict:
        """Get statistics for current user (all roles)"""
        try:
            # 1. Get announcements (superadmin sees all, others see department-specific + global)
            announcements_data = self._get_user_announcements(department_id, role)
            
            # 2. Get weekly booking hours
            weekly_hours = self.stats_repository.get_weekly_booking_hours(user_id)
            
            # 3. Get favorite space
            favorite_space = self.stats_repository.get_favorite_space(user_id)
            
            # 4. Get todo list from assignments and tasks
            todo_list = self._get_user_todo_list(user_id)
            
            return {
                'success': True,
                'data': {
                    'announcements': announcements_data,
                    'weekly_booking_hours': weekly_hours,
                    'favorite_space': favorite_space,
                    'todo_list': todo_list
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_user_announcements(self, department_id: int, role: str = 'employee') -> list:
        """Get announcements for user (superadmin sees all, others see department-specific + global)"""
        announcements = []
        
        # Superadmin can see ALL announcements
        if role == 'superadmin':
            all_announcements = self.announcement_repository.get_all()
        else:
            # Get global announcements (department_id is NULL)
            global_announcements = self.announcement_repository.get_company_wide()
            
            # Get department-specific announcements if user has department
            department_announcements = []
            if department_id:
                department_announcements = self.announcement_repository.get_by_department(department_id)
            
            # Combine announcements
            all_announcements = global_announcements + department_announcements
        
        # Sort by created_at descending
        all_announcements.sort(key=lambda x: x.created_at, reverse=True)
        
        # Superadmin can see more announcements (10), others see 5
        limit = 10 if role == 'superadmin' else 5
        
        # Limit to most recent announcements
        for announcement in all_announcements[:limit]:
            creator = self.user_repository.get_by_id(announcement.created_by)
            announcement_data = {
                'id': announcement.id,
                'title': announcement.title,
                'description': announcement.description,
                'creator_name': creator.username if creator else 'Unknown',
                'created_at': announcement.created_at.isoformat() if announcement.created_at else None
            }
            
            # Include department info for superadmin
            if role == 'superadmin':
                if announcement.department_id:
                    department = self.department_repository.get_by_id(announcement.department_id)
                    announcement_data['department_id'] = announcement.department_id
                    announcement_data['department_name'] = department.name if department else 'Unknown'
                else:
                    announcement_data['department_id'] = None
                    announcement_data['department_name'] = 'Company Wide'
            
            announcements.append(announcement_data)
        
        return announcements
    
    def _get_user_todo_list(self, user_id: int) -> Dict:
        """Get todo list from user's assigned tasks (both complete and incomplete)"""
        # Get all tasks assigned to this user
        tasks = self.task_repository.get_by_user(user_id)
        
        # Enrich tasks with assignment details
        todo_items = []
        for task in tasks:
            assignment = self.assignment_repository.get_by_id(task.assignment_id)
            if assignment:
                todo_items.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_priority': task.priority,
                    'is_done': task.is_done,
                    'assignment_id': assignment.id,
                    'assignment_title': assignment.title,
                    'assignment_due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'created_at': task.created_at.isoformat() if task.created_at else None
                })
        
        # Sort by completion status (incomplete first), then by assignment due_date, then by priority
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        todo_items.sort(key=lambda x: (
            x['is_done'],  # False (incomplete) comes before True (complete)
            x['assignment_due_date'] if x['assignment_due_date'] else '9999-12-31',
            priority_order.get(x['task_priority'], 4)
        ))
        
        # Count completed and incomplete tasks
        completed_count = len([task for task in todo_items if task['is_done']])
        incomplete_count = len([task for task in todo_items if not task['is_done']])
        
        return {
            'total_tasks': len(todo_items),
            'completed_tasks': completed_count,
            'incomplete_tasks': incomplete_count,
            'tasks': todo_items[:20]  # Limit to 20 most recent tasks
        }
