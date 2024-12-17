@echo off
echo Starting AI Defense System...

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Create a new directory for logs if it doesn't exist
if not exist "logs" mkdir logs

REM Check if Redis is running
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Redis Server is already running...
) else (
    echo Starting Redis Server...
    start "Redis Server" Redis\redis-server.exe
)

REM Wait for Redis to be ready
timeout /t 2 /nobreak > nul

REM Start Celery Worker
echo Starting Celery Worker...
start "Celery Worker" cmd /c "celery -A ai_defense worker --pool=solo -l info"

REM Start Celery Beat
echo Starting Celery Beat...
start "Celery Beat" cmd /c "celery -A ai_defense beat -l info"

REM Start Django Development Server
echo Starting Django Server...
start "Django Server" cmd /c "python manage.py runserver"

echo.
echo AI Defense System is starting up...
echo.
echo Access points:
echo - Dashboard: http://localhost:8000
echo.
echo Services are now running in separate windows.
echo Press Ctrl+C in individual windows to stop specific services.
echo Press any key in this window to stop all services (except Redis)...
pause > nul

echo.
echo Shutting down services...
taskkill /F /FI "WindowTitle eq Celery Worker*" /T
taskkill /F /FI "WindowTitle eq Celery Beat*" /T
taskkill /F /FI "WindowTitle eq Django Server*" /T

echo.
echo All services have been stopped (Redis is still running).
timeout /t 3
