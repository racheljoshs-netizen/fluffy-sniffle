
import os
import subprocess
import sys

def test_scout():
    print("Testing Scout-Alpha Shim...")
    
    # Ensure we have a key for testing, or rely on system env
    # os.environ["OPENROUTER_API_KEY"] = "..." # Don't hardcode if possible
    
    cmd = [sys.executable, "E:/G/agents/scout_shim.py", "Briefly explain the 'In-Between' concept in 1 sentence."]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("STDOUT:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("STDERR:", e.stderr)
        print("Test Failed.")

if __name__ == "__main__":
    test_scout()
