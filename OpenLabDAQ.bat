@echo off

REM Open the folder containing this batch file.
cd /d "%~dp0"

REM Start OpenLabDAQ without displaying a terminal window.
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0GUI\gui.py"