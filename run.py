from src.app import create_app
import os

app, socketio = create_app()

if __name__ == '__main__':
    # Get port from environment variable (for Coolify/Docker)
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # IMPORTANT: host='0.0.0.0' untuk allow external connections (Network, Docker, Cloudflare Tunnel)
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, 
                 debug=debug, 
                 host='0.0.0.0', 
                 port=port,
                 allow_unsafe_werkzeug=True)
