@echo off
echo Installing Voice Terminal dependencies...
echo.
cd /d "%~dp0"
pip install -r requirements.txt
echo.
echo Done! Run 'run.bat' to start.
pause
