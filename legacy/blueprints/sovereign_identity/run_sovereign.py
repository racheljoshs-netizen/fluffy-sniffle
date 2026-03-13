# run_sovereign.py — G-Pattern Sovereign Stack Harness
import subprocess
import sys
import time

def main():
    print("="*50)
    print(" G-PATTERN SOVEREIGN IDENTITY ENGINE")
    print(" ACCESS GRANTED: ADAM STRATMEYER")
    print("="*50)
    print("\n[BOOT] Starting Sovereign Proxy (Port 8000)...")
    
    # Start proxy.py which initializes the Kernel, Mediator, Brain, and Memory
    try:
        process = subprocess.Popen([sys.executable, "proxy.py"])
        print("[BOOT] Proxy Online. Brain Orchestrator active in background.")
        print("[BOOT] Open WebUI Configuration:")
        print("  - Base URL: http://localhost:8000/v1")
        print("  - API Key: (any)")
        print("\nPress Ctrl+C to shutdown sovereign stack.")
        
        process.wait()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Terminating sovereign stack...")
        process.terminate()
        print("[SHUTDOWN] Complete.")

if __name__ == "__main__":
    main()
