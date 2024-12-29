import os
import sys
import subprocess
import platform
import venv
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7) or sys.version_info >= (3, 13):
        print("Error: This project requires Python version between 3.7 and 3.12")
        print(f"Current Python version: {platform.python_version()}")
        sys.exit(1)

def find_nodejs():
    """Find Node.js executable in common locations"""
    node_paths = [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files (x86)\nodejs\node.exe",
        os.path.join(os.getenv('APPDATA', ''), 'npm', 'node.exe'),
        os.path.join(os.getenv('PROGRAMFILES', ''), 'nodejs', 'node.exe'),
        os.path.join(os.getenv('PROGRAMFILES(X86)', ''), 'nodejs', 'node.exe'),
    ]
    
    node_path = None
    for path in node_paths:
        if os.path.exists(path):
            node_path = path
            break
    
    if not node_path:
        print("\nError: Node.js not found in common locations")
        print("Please install Node.js from: https://nodejs.org/")
        return False
    
    node_dir = os.path.dirname(node_path)
    os.environ['PATH'] = node_dir + os.pathsep + os.environ.get('PATH', '')
    
    try:
        # Try running node and npm with the updated PATH
        node_version = subprocess.run([node_path, "--version"], capture_output=True, text=True, check=True)
        npm_path = os.path.join(node_dir, "npm.cmd")
        npm_version = subprocess.run([npm_path, "--version"], capture_output=True, text=True, check=True)
        print(f"Found Node.js {node_version.stdout.strip()}")
        print(f"Found npm {npm_version.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError running Node.js commands: {str(e)}")
        print("Please ensure Node.js is properly installed")
        return False
    except Exception as e:
        print(f"\nUnexpected error checking Node.js: {str(e)}")
        return False

def check_venv():
    """Check if virtual environment exists and is properly set up"""
    venv_path = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_path):
        return False
    
    # Check for key files/directories that indicate a proper venv
    if platform.system() == "Windows":
        key_files = ["Scripts/python.exe", "Scripts/pip.exe"]
    else:
        key_files = ["bin/python", "bin/pip"]
    
    return all(os.path.exists(os.path.join(venv_path, f)) for f in key_files)

def create_venv(venv_path):
    """Create a virtual environment if it doesn't exist"""
    if not check_venv():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)

def get_python_executable():
    """Get the appropriate Python executable path"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    return os.path.join("venv", "bin", "python")

def check_dependencies_installed():
    """Check if dependencies are already installed"""
    try:
        # Try importing key packages
        import fastapi
        import uvicorn
        return True
    except ImportError:
        return False

def install_frontend_dependencies():
    """Install frontend dependencies"""
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("\nInstalling frontend dependencies...")
        try:
            # Use shell=True for Windows to handle paths with spaces
            if platform.system() == "Windows":
                subprocess.run(f'cd "{frontend_dir}" && npm install', shell=True, check=True)
            else:
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing frontend dependencies: {str(e)}")
            return False
    return True

def install_dependencies():
    """Install both frontend and backend dependencies"""
    python_exe = get_python_executable()
    
    # Only install backend dependencies if not already installed
    if not check_dependencies_installed():
        print("\nInstalling backend dependencies...")
        backend_req = os.path.join("backend", "requirements.txt")
        if os.path.exists(backend_req):
            try:
                subprocess.run([python_exe, "-m", "pip", "install", "-r", backend_req], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error installing backend dependencies: {str(e)}")
                return False
        else:
            print("Error: backend/requirements.txt not found")
            return False
    
    # Install frontend dependencies if node_modules doesn't exist
    if not install_frontend_dependencies():
        return False
    
    return True

def start_frontend():
    """Start frontend server"""
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    print("\nStarting frontend server...")
    try:
        # Use shell=True for Windows to handle paths with spaces
        if platform.system() == "Windows":
            process = subprocess.Popen(f'cd "{frontend_dir}" && npm start', shell=True)
        else:
            process = subprocess.Popen(["npm", "start"], cwd=frontend_dir)
        return process
    except Exception as e:
        print(f"Error starting frontend server: {str(e)}")
        return None

def start_servers():
    """Start both frontend and backend servers"""
    python_exe = get_python_executable()
    
    print("\nStarting backend server...")
    # Start backend server
    backend_cmd = [python_exe, "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Wait a bit to check if the server starts successfully
        time.sleep(2)
        if backend_process.poll() is not None:
            # Process has terminated
            _, stderr = backend_process.communicate()
            print(f"Error starting backend server: {stderr}")
            return None, None
    except Exception as e:
        print(f"Error starting backend server: {str(e)}")
        return None, None
    
    print("Backend server started successfully!")
    
    # Start frontend server
    frontend_process = start_frontend()
    if frontend_process is None:
        backend_process.terminate()
        return None, None
    
    print("Frontend server started successfully!")
    return backend_process, frontend_process

def main():
    print("\nStarting AI Defense System...")
    
    # Check Python version
    check_python_version()
    
    # Check Node.js installation
    if not find_nodejs():
        sys.exit(1)
    
    # Create virtual environment if it doesn't exist
    venv_path = os.path.join(os.getcwd(), "venv")
    create_venv(venv_path)
    
    # Install dependencies only if needed
    if not check_venv() or not check_dependencies_installed():
        if not install_dependencies():
            print("Failed to install dependencies. Exiting...")
            sys.exit(1)
    
    print("\nStarting servers...")
    
    try:
        backend_process, frontend_process = start_servers()
        if backend_process is None or frontend_process is None:
            print("\nFailed to start servers. Please check the error messages above.")
            sys.exit(1)
            
        print("\nServers started successfully!")
        print("Backend running on http://127.0.0.1:8000")
        print("Frontend running on http://localhost:3000")
        print("\nIf the browser doesn't open automatically, visit:")
        print("http://localhost:3000")
        
        # Try to open the browser
        try:
            webbrowser.open("http://localhost:3000")
        except:
            pass
        
        # Keep the script running
        while True:
            if backend_process.poll() is not None:
                print("\nBackend server stopped unexpectedly")
                frontend_process.terminate()
                break
            if frontend_process.poll() is not None:
                print("\nFrontend server stopped unexpectedly")
                backend_process.terminate()
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
