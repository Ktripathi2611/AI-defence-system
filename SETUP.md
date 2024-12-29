# AI Defense System Setup Guide

## Prerequisites

### 1. Install Python
- Python 3.7 or higher is required
- Current version: Python 3.12

### 2. Install Node.js
1. Download Node.js LTS version from [https://nodejs.org/](https://nodejs.org/)
2. Run the installer
3. During installation:
   - Check "Automatically install the necessary tools" when prompted
   - Click "Next" through the installation steps
   - Wait for the installation to complete
4. Verify installation:
   - Open a new Command Prompt
   - Run: `node --version`
   - Run: `npm --version`
   - If both commands show version numbers, installation was successful

## Setting Up the Project

1. Open Command Prompt in the project directory
2. Run: `python start.py`
   - This will:
     - Create a Python virtual environment
     - Install Python dependencies
     - Install Node.js dependencies
     - Start both backend and frontend servers

## Troubleshooting

### If Node.js is not found
1. Make sure you've installed Node.js
2. Close and reopen Command Prompt
3. Try running `node --version` again
4. If still not working, try:
   - Uninstall Node.js
   - Restart computer
   - Install Node.js again

### If Python dependencies fail to install
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Try running `start.py` again

### If servers won't start
1. Make sure ports 3000 and 8000 are not in use
2. Check if you have antivirus blocking the connections
3. Try running the servers individually:
   - Backend: `cd backend && python -m uvicorn main:app --reload`
   - Frontend: `cd frontend && npm start`

## Default URLs
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs
