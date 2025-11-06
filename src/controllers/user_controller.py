from flask import request, jsonify
from src.usecases.user_usecase import UserUseCase

class UserController:
    """Controller to handle User requests"""
    
    def __init__(self):
        self.user_usecase = UserUseCase()
    
    def get_users(self):
        """Handler to get all users"""
        result = self.user_usecase.get_all_users()
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def get_user(self, user_id):
        """Handler to get user by ID"""
        result = self.user_usecase.get_user_by_id(user_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    
    def create_user(self):
        """Handler to create a new user"""
        data = request.get_json()
        
        name = data.get('name') if data else None
        email = data.get('email') if data else None
        
        result = self.user_usecase.create_user(name=name, email=email)
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    def update_user(self, user_id):
        """Handler to update user"""
        data = request.get_json()
        
        name = data.get('name') if data else None
        email = data.get('email') if data else None
        
        result = self.user_usecase.update_user(user_id=user_id, name=name, email=email)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    def delete_user(self, user_id):
        """Handler to delete user"""
        result = self.user_usecase.delete_user(user_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
