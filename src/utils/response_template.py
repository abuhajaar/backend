"""
Response templates untuk standardisasi HTTP responses
"""

from flask import jsonify
from typing import Any, Dict, Optional

class ResponseTemplate:
    """Class untuk membuat standardized HTTP responses"""
    
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
    def bad_request(error: str = "Bad request", details: Optional[Dict] = None):
        """
        Bad Request response (400)
        """
        response = {
            'success': False,
            'error': error,
            'status_code': 400
        }
        
        if details:
            response['details'] = details
        
        return jsonify(response), 400
    
    @staticmethod
    def unauthorized(error: str = "Unauthorized access"):
        """
        Unauthorized response (401)
        """
        response = {
            'success': False,
            'error': error,
            'status_code': 401,
            'message': 'Authentication required. Please login to access this resource.'
        }
        
        return jsonify(response), 401
    
    @staticmethod
    def forbidden(error: str = "Access forbidden"):
        """
        Forbidden response (403)
        """
        response = {
            'success': False,
            'error': error,
            'status_code': 403,
            'message': 'You do not have permission to access this resource.'
        }
        
        return jsonify(response), 403
    
    @staticmethod
    def not_found(error: str = "Resource not found", resource: str = None):
        """
        Not Found response (404)
        """
        response = {
            'success': False,
            'error': error,
            'status_code': 404
        }
        
        if resource:
            response['message'] = f'{resource} not found'
        else:
            response['message'] = 'The requested resource was not found on this server'
        
        return jsonify(response), 404
    
    @staticmethod
    def internal_error(error: str = "Internal server error", details: Optional[str] = None):
        """
        Internal Server Error response (500)
        """
        response = {
            'success': False,
            'error': error,
            'status_code': 500,
            'message': 'An unexpected error occurred. Please try again later.'
        }
        
        if details:
            response['details'] = details
        
        return jsonify(response), 500
    
    @staticmethod
    def validation_error(errors: Dict[str, list]):
        """
        Validation Error response (422)
        """
        response = {
            'success': False,
            'error': 'Validation failed',
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

def error_response(status_code: int, error: str, **kwargs):
    """Generic error response"""
    if status_code == 400:
        return ResponseTemplate.bad_request(error, kwargs.get('details'))
    elif status_code == 401:
        return ResponseTemplate.unauthorized(error)
    elif status_code == 403:
        return ResponseTemplate.forbidden(error)
    elif status_code == 404:
        return ResponseTemplate.not_found(error, kwargs.get('resource'))
    elif status_code == 500:
        return ResponseTemplate.internal_error(error, kwargs.get('details'))
    else:
        return jsonify({
            'success': False,
            'error': error,
            'status_code': status_code
        }), status_code
