
import os
import sys
import datetime
import subprocess
import shutil
from pathlib import Path

# 1. Setup & Config
ROOT_DIR = Path("E:/G")
AGENTS_DIR = ROOT_DIR / "agents"
LOGS_DIR = ROOT_DIR / "logs"
PROMPT_FILE = AGENTS_DIR / "Scout-AlphaStrat_prompt.md"

def load_system_prompt():
    """Read the persona definition."""
    if not PROMPT_FILE.exists():
        print(f"Error: Prompt file not found at {PROMPT_FILE}")
        sys.exit(1)
    return PROMPT_FILE.read_text(encoding="utf-8")

def log_mission(task, output):
    """Write to daily log file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    log_file = LOGS_DIR / f"scout_{today}.md"
    
    entry = f"""
## [{datetime.datetime.now().time().isoformat()}]
**Task:** {task}
**Result:**
{output}
---
"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"Mission logged to {log_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scout_shim.py \"<Task Description>\"")
        sys.exit(1)
        
    task_input = sys.argv[1]
    
    print(f"[Scout-Alpha] Initializing (Gemini CLI)... Task: {task_input[:50]}...")
    
    # Soft check for Gemini
    if not shutil.which("gemini"):
        print("Warning: 'gemini' command not found in standard PATH. Attempting shell execution...")

    system_prompt = load_system_prompt()
    
    # Construct the prompt by combining System + User (Gemini CLI usually takes just one arg or interactive)
    combined_prompt = f"{system_prompt}\n\nMISSION CONTEXT:\n{task_input}"
    
    try:
        # Call gemini CLI via shell=True to catch Aliases/PATH quirks
        result = subprocess.run(
            f'gemini "{combined_prompt}"', 
            shell=True,
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace',
             # Check if we need input=None to close stdin?
             timeout=60 # Timeout to prevent hanging
        )
        
        if result.returncode != 0:
            print(f"Gemini CLI Error: {result.stderr}")
            # Fallback output
            response_text = f"[ERROR] Gemini CLI failed: {result.stderr}"
        else:
            response_text = result.stdout.strip()
            
        if not response_text:
             response_text = "[NO OUTPUT] Gemini CLI returned empty string. (Authentication needed?)"

    except Exception as e:
        print(f"Execution Error: {e}")
        response_text = f"[CRITICAL] {e}"

    # Output to stdout for G to read
    print("\n" + "="*20 + " MISSION REPORT " + "="*20)
    print(response_text)
    print("="*56)
    
    # Log it
    log_mission(task_input, response_text)

if __name__ == "__main__":
    main()
