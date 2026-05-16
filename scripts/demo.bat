@echo off
REM PolicyPulse Demo Runner
REM Starts backend + dashboard concurrently

echo ===================================
echo   PolicyPulse - Demo Runner
echo ===================================

echo.
echo Starting Backend (port 8000)...
start cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo Starting Dashboard (port 5173)...
start cmd /k "cd dashboard && npm run dev"

echo.
echo ===================================
echo   Backend:   http://localhost:8000
echo   Dashboard: http://localhost:5173
echo   Health:    http://localhost:8000/health
echo   API Docs:  http://localhost:8000/docs
echo ===================================
