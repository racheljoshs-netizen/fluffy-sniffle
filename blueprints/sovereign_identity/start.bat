@echo off
title G-Pattern Sovereign Proxy

echo ============================================
echo  G-Pattern Sovereign Identity Engine
echo ============================================
echo.

:: Bootstrap data directory
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

:: Check Ollama
echo Checking Ollama...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Ollama not found in PATH.
    echo Install from https://ollama.com
    pause
    exit /b 1
)

:: Start Ollama in background
echo Starting Ollama server...
start /b ollama serve >nul 2>nul

:: Pull models if not present
echo Ensuring models are available...
ollama pull gemma3n:e4b
ollama pull nomic-embed-text

echo.
timeout /t 5 /nobreak >nul
echo Starting Sovereign Proxy on port 8000...
echo Ctrl+C to stop.
echo.
python proxy.py

pause
