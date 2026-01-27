from flask import request
from src.usecases.task_usecase import TaskUseCase
from src.utils.response_template import ResponseTemplate

class TaskController:
    """Controller to handle Task requests"""
    
    def __init__(self):
        self.task_usecase = TaskUseCase()
        self.response = ResponseTemplate()
    
    def get_tasks_by_assignment(self, assignment_id):
        """Handler for manager to get all tasks for specific assignment"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            result = self.task_usecase.get_tasks_by_assignment(
                assignment_id=assignment_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Tasks retrieved successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to retrieve tasks')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve tasks: {str(e)}"
            )
    
    def create_task(self, assignment_id):
        """Handler for manager to create task for specific assignment"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            # Get request body
            data = request.get_json()
            
            result = self.task_usecase.create_task(
                assignment_id=assignment_id,
                title=data.get('title'),
                priority=data.get('priority'),
                user_id=data.get('user_id'),
                is_done=data.get('is_done', False),
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Task created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create task')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to create task: {str(e)}"
            )
    
    def update_task(self, task_id):
        """Handler for manager and employee to update task"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            user_id = current_user.get('user_id')
            department_id = current_user.get('department_id')
            role = current_user.get('role')
            
            # Get request body
            data = request.get_json()
            
            result = self.task_usecase.update_task(
                task_id=task_id,
                title=data.get('title'),
                priority=data.get('priority'),
                user_id_to_assign=data.get('user_id'),
                is_done=data.get('is_done'),
                current_user_id=user_id,
                current_user_department_id=department_id,
                current_user_role=role
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Task updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update task')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to update task: {str(e)}"
            )
    
    def delete_task(self, task_id):
        """Handler for manager to delete task"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            result = self.task_usecase.delete_task(
                task_id=task_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.success(
                    data=None,
                    message="Task deleted successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to delete task')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to delete task: {str(e)}"
            )
