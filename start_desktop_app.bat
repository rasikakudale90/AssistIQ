@echo off
title AssistIQ Desktop Application Launcher
echo ===================================================
echo   AssistIQ AI-Assisted IT Helpdesk - Desktop App
echo ===================================================
echo.
echo Starting AssistIQ native desktop application window...
cd /d "%~dp0frontend"
call npm run desktop
pause
