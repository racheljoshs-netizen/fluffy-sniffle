import subprocess
import time
import os
import sys
from pathlib import Path

# Paths to core components
ROOT_DIR = Path("e:/G")
CHARIOT_DIR = ROOT_DIR / "chariot"
ENGINE_SCRIPT = CHARIOT_DIR / "chariot_engine.py"
PROVIDENCE_SCRIPT = CHARIOT_DIR / "providence_core_alpaca.py"

def is_process_running(script_name):
    """Check if a python process with the given script name is running using PowerShell."""
    try:
        # Use PowerShell to get full command line
        cmd = f'powershell "Get-CimInstance Win32_Process -Filter \\"Name=\'python.exe\'\\" | Where-Object {{ $_.CommandLine -like \'*{script_name}*\' }} | Select-Object -ExpandProperty ProcessId"'
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        return len(output) > 0
    except Exception:
        return False

def start_service(name, script_path, cwd):
    """Start a python script as a background process."""
    if is_process_running(script_path.name):
        print(f"[✓] {name} is already breathing.")
        return None
    
    print(f"[!] Starting {name}...")
    try:
        # Launch in background with redirects to logs
        log_file = ROOT_DIR / "logs" / f"{name.lower()}.log"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, "a") as f:
            proc = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(cwd),
                stdout=f,
                stderr=f,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
        print(f"[✓] {name} launched (PID: {proc.pid}). Logs: {log_file}")
        return proc
    except Exception as e:
        print(f"[X] Failed to start {name}: {e}")
        return None

def main():
    print("="*60)
    print("CHIEF-Strat :: Master Orchestrator (GUARDIAN MODE)")
    print("="*60)
    print(f"Substrate: {os.name} (Windows Detected)")
    print("Continuous monitoring active. Press Ctrl+C to terminate.")
    print("-" * 60)

    try:
        while True:
            t = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 1. Start/Verify CHARIOT Engine
            start_service("CHARIOT Engine", ENGINE_SCRIPT, CHARIOT_DIR)
            
            # 2. Start/Verify PROVIDENCE-Core
            start_service("PROVIDENCE-Core", PROVIDENCE_SCRIPT, CHARIOT_DIR)

            # Sleep interval (5 minutes)
            time.sleep(300)
    except KeyboardInterrupt:
        print("\n[!] Orchestrator shutting down. Background processes will remain running.")
        print("="*60)

if __name__ == "__main__":
    main()
