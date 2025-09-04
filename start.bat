@echo off
echo ================================
echo Starting EcoLearn AI Backend...
echo ================================
echo.

:: Optional: activate virtual environment if you have one
:: call venv\Scripts\activate

:: Start backend server in a new terminal window
start "" cmd /k "uvicorn main:app --reload --host 127.0.0.1 --port 8000"

:: Wait a few seconds so the server starts
timeout /t 5 >nul

:: Open frontend chat.html in default browser
start "" "index.html"

echo.
echo Backend is running! Frontend opened in browser.
echo Use Ctrl+C in the server window to stop the backend.
echo.
pause
