@echo off
echo 🚀 Starting Research Paper Review Tokenizer Backend...
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create uploads directory
if not exist "uploads\papers" mkdir uploads\papers

echo.
echo ✅ Setup complete!
echo 🌐 Starting server at http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.

REM Start the server
python main.py

pause
