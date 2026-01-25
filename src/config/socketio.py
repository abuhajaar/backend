from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    socketio.init_app(app, 
                      cors_allowed_origins="*",
                      async_mode='threading',
                      logger=True,
                      engineio_logger=True)
    return socketio
