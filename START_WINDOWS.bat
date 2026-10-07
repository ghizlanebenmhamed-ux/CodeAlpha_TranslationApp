@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (set "PYTHON_CMD=python") else (set "PYTHON_CMD=py")
%PYTHON_CMD% -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe chatbot.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Setup or startup failed. Read the error above. Install Python with Tkinter and internet access for package installation.
pause
