from src.app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (for Coolify/Docker)
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host='localhost', port=port)
