import os
import subprocess
import sys

# --- JULES SHIM (THE MECHANIC) ---
# Bypasses the MCP ENOENT error by hardcoding the global npm path.

JULES_CMD = r"C:\Users\AIS\AppData\Roaming\npm\jules.cmd"

def run_jules_task(repo_name, description):
    print(f"[MECHANIC] Engaging Jules via direct shim for {repo_name}...")
    
    # We can use the 'jules new' command
    # jules new --repo <repo> "<description>"
    cmd = [JULES_CMD, "new", "--repo", repo_name, description]
    
    print(f"[MECHANIC] Executing: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=os.environ.copy()
        )
        
        for line in iter(process.stdout.readline, ''):
            print(f"[JULES] {line.strip()}")
            
        process.stdout.close()
        process.wait()
        print(f"[MECHANIC] Jules task initiated with return code {process.returncode}.")
    except Exception as e:
        print(f"[ERROR] Mechanic choked on Jules shim: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python jules_shim.py <repo_name> <task_description>")
        sys.exit(1)
        
    run_jules_task(sys.argv[1], sys.argv[2])
