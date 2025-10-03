@echo off
REM Activation script for the virtual environment (Windows)
REM Usage: activate.bat

echo Activating virtual environment...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat && pip install --upgrade pip && pip install -r requirements.txt
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

echo Virtual environment activated!
echo You can now run: python main.py
echo To deactivate, run: deactivate
