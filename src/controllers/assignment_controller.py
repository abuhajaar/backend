from flask import request
from src.usecases.assignment_usecase import AssignmentUseCase
from src.utils.response_template import ResponseTemplate

class AssignmentController:
    """Controller to handle Assignment requests"""
    
    def __init__(self):
        self.assignment_usecase = AssignmentUseCase()
        self.response = ResponseTemplate()
    
    def get_assignments(self):
        """Handler for manager to get all assignments for their department"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_department_id = current_user.get('department_id')
            
            result = self.assignment_usecase.get_assignments_for_department(manager_department_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Assignments retrieved successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to retrieve assignments')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to retrieve assignments: {str(e)}"
            )
    
    def create_assignment(self):
        """Handler for manager to create assignment"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            # Get request body
            data = request.get_json()
            
            result = self.assignment_usecase.create_assignment(
                title=data.get('title'),
                description=data.get('description'),
                due_date=data.get('due_date'),
                created_by=manager_id,
                department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Assignment created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create assignment')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to create assignment: {str(e)}"
            )
    
    def update_assignment(self, assignment_id):
        """Handler for manager to update assignment"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            # Get request body
            data = request.get_json()
            
            result = self.assignment_usecase.update_assignment(
                assignment_id=assignment_id,
                title=data.get('title'),
                description=data.get('description'),
                due_date=data.get('due_date'),
                manager_id=manager_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Assignment updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update assignment')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to update assignment: {str(e)}"
            )
    
    def delete_assignment(self, assignment_id):
        """Handler for manager to delete assignment"""
        try:
            # Get current user from JWT token
            current_user = request.current_user
            manager_id = current_user.get('user_id')
            manager_department_id = current_user.get('department_id')
            
            result = self.assignment_usecase.delete_assignment(
                assignment_id=assignment_id,
                manager_id=manager_id,
                manager_department_id=manager_department_id
            )
            
            if result['success']:
                return self.response.success(
                    data=None,
                    message="Assignment deleted successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to delete assignment')
            )
        except Exception as e:
            return self.response.internal_error(
                message=f"Failed to delete assignment: {str(e)}"
            )
