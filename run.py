import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path
from src import create_app

def is_redis_running():
    """Check if Redis server is running"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'redis-server.exe':
            return True
    return False

def start_redis():
    """Start Redis server"""
    redis_path = Path(__file__).parent / 'Redis' / 'redis-server.exe'
    if not redis_path.exists():
        print("Error: Redis server not found at", redis_path)
        sys.exit(1)
    
    if not is_redis_running():
        print("Starting Redis server...")
        subprocess.Popen([str(redis_path)], 
                        cwd=redis_path.parent,
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(2)  # Wait for Redis to start
    else:
        print("Redis server is already running")

def start_django():
    """Start Django development server"""
    print("Starting Django server...")
    manage_py = Path(__file__).parent / 'manage.py'
    if not manage_py.exists():
        print("Error: manage.py not found at", manage_py)
        sys.exit(1)

    # Activate virtual environment
    venv_path = Path(__file__).parent / 'venv'
    if venv_path.exists():
        if sys.platform == 'win32':
            python_path = venv_path / 'Scripts' / 'python.exe'
        else:
            python_path = venv_path / 'bin' / 'python'
    else:
        python_path = sys.executable

    app = create_app()
    django_process = subprocess.Popen([str(python_path), str(manage_py), 'runserver'],
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)
    return django_process

def cleanup(django_process):
    """Cleanup function to handle server shutdown"""
    print("\nShutting down servers...")
    
    # Stop Django server
    if django_process:
        django_process.terminate()
        django_process.wait()
    
    # Stop Redis server
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'redis-server.exe':
            proc.terminate()

def main():
    try:
        # Start Redis
        start_redis()
        
        # Start Django
        django_process = start_django()
        
        print("\nAll servers are running!")
        print("Access the application at: http://localhost:8000")
        print("Press Ctrl+C to stop all servers...")
        
        # Keep the script running and handle Ctrl+C
        django_process.wait()
    
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(django_process)
        print("Servers shut down successfully")

if __name__ == "__main__":
    main()
