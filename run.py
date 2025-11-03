from src.app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (for Coolify/Docker)
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # IMPORTANT: host='0.0.0.0' untuk allow external connections (Docker, Cloudflare Tunnel)
    app.run(debug=debug, host='0.0.0.0', port=port)
