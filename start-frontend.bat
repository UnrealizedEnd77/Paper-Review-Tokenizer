@echo off
echo 🎨 Starting Research Paper Review Tokenizer Frontend...
echo.

cd frontend

echo 🌐 Starting server at http://localhost:3000
echo 🔗 Open your browser and navigate to http://localhost:3000
echo.
echo ⚠️  Make sure the backend is running at http://localhost:8000
echo.

REM Start Python's built-in HTTP server
python -m http.server 3000

pause
