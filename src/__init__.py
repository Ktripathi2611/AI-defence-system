from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configure app
    if test_config is None:
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-please-change'),
            SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///aidefense.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
            ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'wav', 'mp3'}
        )
    else:
        app.config.update(test_config)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register core blueprints
    from .routes.main import main_bp
    from .routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
