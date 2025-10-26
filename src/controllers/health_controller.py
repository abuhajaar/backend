from flask import jsonify

class HealthController:
    """Controller untuk health check"""
    
    def health_check(self):
        """Handler untuk health check"""
        return jsonify({
            'success': True,
            'message': 'Server is running',
            'database': 'connected'
        }), 200
