from flask import request, jsonify
from src.usecases.department_usecase import DepartmentUseCase
from src.utils.response_template import ResponseTemplate

class DepartmentController:
    """Controller to handle Department requests"""
    
    def __init__(self):
        self.department_usecase = DepartmentUseCase()
        self.response = ResponseTemplate()
    
    def get_departments(self):
        """Handler to get all departments"""
        try:
            result = self.department_usecase.get_all_departments()
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Departments retrieved successfully"
                )
            return self.response.internal_server_error(
                message=result.get('error', 'Failed to retrieve departments')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve departments: {str(e)}"
            )
    
    def get_department(self, department_id):
        """Handler to get department by ID"""
        try:
            result = self.department_usecase.get_department_by_id(department_id)
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Department retrieved successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Department with ID {department_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to retrieve department: {str(e)}"
            )
    
    def create_department(self):
        """Handler to create a new department"""
        try:
            data = request.get_json()
            
            name = data.get('name') if data else None
            description = data.get('description') if data else None
            
            result = self.department_usecase.create_department(
                name=name, 
                description=description
            )
            
            if result['success']:
                return self.response.created(
                    data=result['data'],
                    message="Department created successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to create department')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to create department: {str(e)}"
            )
    
    def update_department(self, department_id):
        """Handler to update department"""
        try:
            data = request.get_json()
            
            name = data.get('name') if data else None
            description = data.get('description') if data else None
            
            result = self.department_usecase.update_department(
                department_id=department_id, 
                name=name,
                description=description
            )
            
            if result['success']:
                return self.response.success(
                    data=result['data'],
                    message="Department updated successfully"
                )
            return self.response.bad_request(
                message=result.get('error', 'Failed to update department')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to update department: {str(e)}"
            )
    
    def delete_department(self, department_id):
        """Handler to delete department"""
        try:
            result = self.department_usecase.delete_department(department_id)
            if result['success']:
                return self.response.success(
                    data=result.get('data'),
                    message="Department deleted successfully"
                )
            return self.response.not_found(
                message=result.get('error', f'Department with ID {department_id} not found')
            )
        except Exception as e:
            return self.response.internal_server_error(
                message=f"Failed to delete department: {str(e)}"
            )
