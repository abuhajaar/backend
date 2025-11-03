"""
Global error handlers untuk Flask application
"""

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from src.utils.response_template import ResponseTemplate

def register_error_handlers(app: Flask):
    """Register all error handlers to Flask app"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request"""
        return ResponseTemplate.bad_request(
            message=str(error) if str(error) != "400 Bad Request: " else "Bad request"
        )
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized"""
        return ResponseTemplate.unauthorized(
            message=str(error) if str(error) != "401 Unauthorized: " else "Unauthorized access"
        )
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden"""
        return ResponseTemplate.forbidden(
            message=str(error) if str(error) != "403 Forbidden: " else "Access forbidden"
        )
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found"""
        return ResponseTemplate.not_found(
            message="Endpoint not found",
            resource=f"'{request.path}'"
        )
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed"""
        return jsonify({
            'success': False,
            'message': f"Method {request.method} not allowed for this endpoint",
            'status_code': 405,
            'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else []
        }), 405
    
    @app.errorhandler(422)
    def validation_error(error):
        """Handle 422 Validation Error"""
        return jsonify({
            'success': False,
            'message': 'Validation failed',
            'status_code': 422,
            'details': str(error)
        }), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        app.logger.error(f'Internal Server Error: {str(error)}')
        return ResponseTemplate.internal_error(
            message="Internal server error",
            details=str(error) if app.debug else None
        )
    
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        """Handle Database errors"""
        app.logger.error(f'Database Error: {str(error)}')
        return ResponseTemplate.internal_error(
            message="Database error occurred",
            details=str(error) if app.debug else None
        )
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle generic exceptions"""
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        
        # Log the error
        app.logger.error(f'Unhandled Exception: {str(error)}', exc_info=True)
        
        # Return 500 error
        return ResponseTemplate.internal_error(
            message="An unexpected error occurred",
            details=str(error) if app.debug else None
        )
    
    return app
