@echo off
:: Aegis Startup Script
:: Launches Watchdog Daemon in background

echo [Aegis] Initializing Active Defense...
cd /d %~dp0

:: Launch Watchdog hidden
start /B python defense\watchdog.py

echo [Aegis] Watchdog is active.
timeout /t 3 >nul
exit
