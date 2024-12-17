@echo off
echo AI Defense System Service Manager
echo ================================

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:menu
cls
echo.
echo Service Control Menu:
echo ------------------
echo 1. Start Dashboard (Django Server)
echo 2. Start Redis Server
echo 3. Start Celery Worker
echo 4. Start Celery Beat
echo 5. Start Flower Monitor
echo 6. Start All Services
echo 7. Check Services Status
echo 0. Exit
echo.

set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" goto start_django
if "%choice%"=="2" goto start_redis
if "%choice%"=="3" goto start_celery_worker
if "%choice%"=="4" goto start_celery_beat
if "%choice%"=="5" goto start_flower
if "%choice%"=="6" goto start_all
if "%choice%"=="7" goto check_status
if "%choice%"=="0" goto end
goto menu

:start_django
echo Starting Django Server...
start "Django Server" cmd /c "python manage.py runserver > logs\django.log 2>&1"
echo Django server started at http://localhost:8000
timeout /t 2 /nobreak > nul
goto menu

:start_redis
echo Checking Redis status...
Redis\redis-cli.exe ping > nul 2>&1
if errorlevel 1 (
    echo Starting Redis Server...
    start "Redis Server" Redis\redis-server.exe Redis\redis.conf
    echo Redis server started
) else (
    echo Redis is already running
)
timeout /t 2 /nobreak > nul
goto menu

:start_celery_worker
echo Starting Celery Worker...
start "Celery Worker" cmd /c "celery -A ai_defence_system worker --pool=solo -l info > logs\celery_worker.log 2>&1"
echo Celery worker started
timeout /t 2 /nobreak > nul
goto menu

:start_celery_beat
echo Starting Celery Beat...
start "Celery Beat" cmd /c "celery -A ai_defence_system beat -l info > logs\celery_beat.log 2>&1"
echo Celery beat started
timeout /t 2 /nobreak > nul
goto menu

:start_flower
echo Starting Flower Monitor...
start "Flower" cmd /c "celery -A ai_defence_system flower > logs\flower.log 2>&1"
echo Flower monitor started at http://localhost:5555
timeout /t 2 /nobreak > nul
goto menu

:start_all
call :start_redis
call :start_celery_worker
call :start_celery_beat
call :start_flower
call :start_django
echo All services started!
timeout /t 2 /nobreak > nul
goto menu

:check_status
echo.
echo Checking Services Status...
echo -------------------------
echo Redis Server:
Redis\redis-cli.exe ping > nul 2>&1
if errorlevel 1 (
    echo [STOPPED]
) else (
    echo [RUNNING]
)

echo Django Server:
netstat -ano | find "8000" > nul
if errorlevel 1 (
    echo [STOPPED]
) else (
    echo [RUNNING]
)

echo Celery Worker:
tasklist /FI "WINDOWTITLE eq Celery Worker" | find "cmd.exe" > nul
if errorlevel 1 (
    echo [STOPPED]
) else (
    echo [RUNNING]
)

echo Celery Beat:
tasklist /FI "WINDOWTITLE eq Celery Beat" | find "cmd.exe" > nul
if errorlevel 1 (
    echo [STOPPED]
) else (
    echo [RUNNING]
)

echo Flower Monitor:
netstat -ano | find "5555" > nul
if errorlevel 1 (
    echo [STOPPED]
) else (
    echo [RUNNING]
)

echo.
pause
goto menu

:end
echo Exiting Service Manager...
exit
