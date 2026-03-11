import os
import sys
import traceback
from config import PROFILE_PATH

def debug_persistence():
    print(f"[Debug] Python: {sys.executable}")
    print(f"[Debug] Profile Path Config: {PROFILE_PATH}")
    print(f"[Debug] Exists: {os.path.exists(PROFILE_PATH)}")
    
    try:
        from core import PhoenixController
        print("[Debug] Module imported.")
        
        phoenix = PhoenixController()
        print("[Debug] Controller instantiated.")
        
        phoenix.launch()
        print("[Debug] Launched.")
        
        phoenix.goto("https://myaccount.google.com/")
        print(f"[Debug] Page Title: {phoenix.page.title()}")
        
        phoenix.close()
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    debug_persistence()
