from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

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
    
    # Initialize extensions
    from .models import init_db
    init_db(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    CORS(app)
    
    # Import and register blueprints
    from .routes.main import main_bp, init_app as init_main
    from .routes.auth import auth_bp
    from .routes.chat import chat_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    # Initialize custom filters
    init_main(app)
    
    # Register custom filters
    from .utils.filters import time_ago
    app.jinja_env.filters['time_ago'] = time_ago

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    from flask import current_app
    with current_app.app_context():
        return User.query.get(int(user_id))
