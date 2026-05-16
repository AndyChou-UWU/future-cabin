@echo off
REM Change to the project directory (using the short 8.3 path to avoid Unicode issues)
cd /d "C:\Users\User\Downloads\PYTHON~2\SMART_~1\smart_cabin_project"
REM Activate the virtual environment if it exists
IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
REM Run Django collectstatic
python manage.py collectstatic --noinput