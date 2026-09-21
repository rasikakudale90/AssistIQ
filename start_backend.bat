@echo off
title AssistIQ Backend Server (FastAPI)
echo ===================================================
echo   AssistIQ AI-Assisted IT Helpdesk - Backend
echo ===================================================
echo.
echo Starting FastAPI server at http://localhost:8000...
cd /d "%~dp0"
set PYTHONPATH=%~dp0
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
