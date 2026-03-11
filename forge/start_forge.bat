@echo off
set CUDA_VISIBLE_DEVICES=0,1
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo [GENESIS] Starting Local Image Backend (Dual RTX 3060 mode)...
cd /d e:\G\forge-backend
venv\Scripts\python.exe main.py --port 8188 --listen 127.0.0.1 --preview-method auto
pause
