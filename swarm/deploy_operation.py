
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sentinels import run_swarm
from scribe import invoke_scribe

def execute_operation():
    print("--- INITIATING OPERATION: ANTI-GRAVITY RECON ---")
    
    task_prime = """
    TARGET: Google's 'Project Anti-Gravity'.
    MISSION:
    1. Research the origins, purpose, and current status of 'Anti-Gravity' within Google/DeepMind.
    2. Focus on: Functionality, code capability, and 'Advance Agentic Coding'.
    3. Gather and synthesize the most valuable points of use to us (AIS).
    """
    
    task_secundus = """
    TARGET: Gemini CLI & Anti-Gravity.
    MISSION:
    1. Research the 'Gemini CLI' specifically.
    2. Investigate its integration and usage within the context of 'Anti-Gravity'.
    3. Look for advanced usage patterns, flags, or hidden capabilities relevant to our operations.
    """
    
    # 1. Deploy Sentinels
    swarm = run_swarm(task_prime, task_secundus)
    print(f"Sentinels deployed. PIDs: {swarm['PRIME'].pid}, {swarm['SECUNDUS'].pid}")
    
    # 2. Wait for Intelligence (Extended for Titan Class Latency)
    print("Waiting 200s for Sentinel intelligence burst...")
    time.sleep(200)
    
    # 3. Harvest Output
    prime_intel = ""
    secundus_intel = ""
    
    for name, proc in swarm.items():
        try:
            # Check if process is still alive
            if proc.poll() is None:
                print(f"{name} is still running. Attempting to capture output...")
            
            stdout, stderr = proc.communicate(timeout=60)
            intel = f"--- {name} RAW INTEL ---\n{stdout}\n"
            print(intel)
            if name == "PRIME": prime_intel = stdout
            if name == "SECUNDUS": secundus_intel = stdout
        except Exception as e:
            print(f"Error harvesting {name}: {e}")
            
    # 4. Invoke Scribe
    if prime_intel or secundus_intel:
        combined_intel = f"{prime_intel}\n\n{secundus_intel}"
        print("Invoking Scribe for Compilation...")
        summary = invoke_scribe(combined_intel, "Project Anti-Gravity and Gemini CLI")
        print(f"\n--- FINAL SCRIBE COMPILATION ---\n{summary}")
    else:
        print("No intelligence gathered to compile.")

if __name__ == "__main__":
    execute_operation()
