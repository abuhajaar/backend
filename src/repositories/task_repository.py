from typing import List, Optional
from src.models.task import Task
from src.config.database import db

class TaskRepository:
    """Repository for Task operations"""
    
    def get_all(self) -> List[Task]:
        """Get all tasks"""
        return Task.query.order_by(Task.created_at.desc()).all()
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        return Task.query.get(task_id)
    
    def get_by_assignment(self, assignment_id: int) -> List[Task]:
        """Get all tasks for specific assignment"""
        return Task.query.filter_by(assignment_id=assignment_id).all()
    
    def get_by_user(self, user_id: int) -> List[Task]:
        """Get all tasks for specific user"""
        return Task.query.filter_by(user_id=user_id).all()
    
    def create(self, task_data: dict) -> Task:
        """Create new task"""
        task = Task(
            title=task_data.get('title'),
            priority=task_data.get('priority', 'medium'),
            assignment_id=task_data.get('assignment_id'),
            user_id=task_data.get('user_id'),
            is_done=task_data.get('is_done', False)
        )
        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)
        return task
    
    def update(self, task_id: int, update_data: dict) -> Optional[Task]:
        """Update task"""
        task = self.get_by_id(task_id)
        if task:
            if 'title' in update_data:
                task.title = update_data['title']
            if 'priority' in update_data:
                task.priority = update_data['priority']
            if 'user_id' in update_data:
                task.user_id = update_data['user_id']
            if 'is_done' in update_data:
                task.is_done = update_data['is_done']
            db.session.commit()
            db.session.refresh(task)
        return task
    
    def delete(self, task_id: int) -> bool:
        """Delete task"""
        task = self.get_by_id(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False
