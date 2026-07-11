@echo off

REM Open the folder containing this batch file.
cd /d "%~dp0"

REM Run with a terminal so Python messages and errors remain visible.
"%~dp0.venv\Scripts\python.exe" "%~dp0GUI\gui.py"

pause