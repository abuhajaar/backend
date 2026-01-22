from flask import Blueprint
from src.controllers.task_controller import TaskController
from src.utils.jwt_helper import token_required, role_required

# Initialize blueprint
task_routes = Blueprint('task_routes', __name__)

# Initialize controller
task_controller = TaskController()

# Manager routes
@task_routes.route('/assignment/<int:assignment_id>', methods=['GET'])
@token_required
@role_required(['manager'])
def get_tasks_by_assignment(assignment_id):
    """Route for manager to get all tasks for specific assignment"""
    return task_controller.get_tasks_by_assignment(assignment_id)

@task_routes.route('/assignment/<int:assignment_id>', methods=['POST'])
@token_required
@role_required(['manager'])
def create_task(assignment_id):
    """Route for manager to create task for specific assignment"""
    return task_controller.create_task(assignment_id)

@task_routes.route('/<int:task_id>', methods=['PUT'])
@token_required
@role_required(['manager','employee'])
def update_task(task_id):
    """Route for manager to update task"""
    return task_controller.update_task(task_id)

@task_routes.route('/<int:task_id>', methods=['DELETE'])
@token_required
@role_required(['manager'])
def delete_task(task_id):
    """Route for manager to delete task"""
    return task_controller.delete_task(task_id)
