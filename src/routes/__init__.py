from flask import Blueprint

# Import blueprints
from .main import main_bp
from .chat import chat_bp
from .auth import auth_bp

# Register all blueprints
def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(auth_bp, url_prefix='/auth')
