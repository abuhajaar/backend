from flask import jsonify

class HealthController:
    """Controller to handle health check"""
    
    def health_check(self):
        """Handler to check health status of the server"""
        return jsonify({
            'success': True,
            'message': 'Server is running',
            'database': 'connected'
        }), 200
