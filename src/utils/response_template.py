from flask import jsonify
from typing import Any, Dict, Optional

class ResponseTemplate:
    """Class for creating standardized HTTP responses"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200):
        """
        Success response template (200, 201, etc.)
        """
        response = {
            'success': True,
            'message': message,
            'status_code': status_code
        }
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def created(data: Any = None, message: str = "Resource created successfully"):
        """
        Created response (201)
        """
        return ResponseTemplate.success(data=data, message=message, status_code=201)
    
    @staticmethod
    def bad_request(message: str = "Bad request", details: Optional[Dict] = None):
        """
        Bad Request response (400)
        """
        response = {
            'success': False,
            'message': message,
            'status_code': 400
        }
        
        if details:
            response['details'] = details
        
        return jsonify(response), 400
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized access"):
        """
        Unauthorized response (401)
        """
        response = {
            'success': False,
            'message': message,
            'status_code': 401
        }
        
        return jsonify(response), 401
    
    @staticmethod
    def forbidden(message: str = "Access forbidden"):
        """
        Forbidden response (403)
        """
        response = {
            'success': False,
            'message': message,
            'status_code': 403
        }
        
        return jsonify(response), 403
    
    @staticmethod
    def not_found(message: str = "Resource not found", resource: str = None):
        """
        Not Found response (404)
        """
        response = {
            'success': False,
            'status_code': 404
        }
        
        if resource:
            response['message'] = f'{resource} not found'
        else:
            response['message'] = message
        
        return jsonify(response), 404
    
    @staticmethod
    def internal_error(message: str = "Internal server error", details: Optional[str] = None):
        """
        Internal Server Error response (500)
        """
        response = {
            'success': False,
            'message': message,
            'status_code': 500
        }
        
        if details:
            response['details'] = details
        
        return jsonify(response), 500
    
    @staticmethod
    def validation_error(errors: Dict[str, list], message: str = "Validation failed"):
        """
        Validation Error response (422)
        """
        response = {
            'success': False,
            'message': message,
            'status_code': 422,
            'errors': errors
        }
        
        return jsonify(response), 422


# Shorthand functions untuk kemudahan
def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Shorthand untuk success response"""
    return ResponseTemplate.success(data, message, status_code)

def created_response(data: Any = None, message: str = "Resource created successfully"):
    """Shorthand untuk created response"""
    return ResponseTemplate.created(data, message)

def error_response(status_code: int, message: str, **kwargs):
    """Generic error response"""
    if status_code == 400:
        return ResponseTemplate.bad_request(message, kwargs.get('details'))
    elif status_code == 401:
        return ResponseTemplate.unauthorized(message)
    elif status_code == 403:
        return ResponseTemplate.forbidden(message)
    elif status_code == 404:
        return ResponseTemplate.not_found(message, kwargs.get('resource'))
    elif status_code == 500:
        return ResponseTemplate.internal_error(message, kwargs.get('details'))
    else:
        return jsonify({
            'success': False,
            'message': message,
            'status_code': status_code
        }), status_code
