from src import create_app, db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create the Flask application instance
app = create_app()
app.app_context().push()  # Ensure we have an application context

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'app': app}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("Starting the AI Defense System...")
    print(f"Access the application at: http://127.0.0.1:{port}")
    print(f"Running in {'debug' if debug else 'production'} mode")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
