@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (set "PYTHON_CMD=python") else (set "PYTHON_CMD=py")
%PYTHON_CMD% server.py
if errorlevel 1 (
echo Startup failed. Install Python and read the error above.
pause
)
