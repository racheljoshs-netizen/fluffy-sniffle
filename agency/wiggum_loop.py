import subprocess
import os
import sys
import json
import time
import re
import httpx
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# --- INITIALIZATION ---
load_dotenv(r'E:\0x\.env')

STATE_FILE = "wiggum_state.json"
LOG_DIR = "wiggum_logs"
MAX_RETRIES = 5

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# --- KEY POOL ---
GOOGLE_KEYS = [
    "AIzaSyAETN8xZun1DgzccRarhF5YM1oZoAAs7nU",
    "AIzaSyBTamag0G50pyt7ZKwv0ELHgAHNmNd7r_A",
    "AIzaSyBcSPhVD-GczK1VUBztL7SJl5vgNhaDWXs",
    "AIzaSyB4tYAzpx-vgXTtnxMUR5hBARcUqO6NFtA",
    "AIzaSyBMhnPaXgBRNcmxgeVfcbiSwB1j_0sw0wc",
    "AIzaSyB32rj6emv5pc01Q7wuMj41rQ-vhdD8CZY",
    "AIzaSyCKiVJ8SebWCf2PgdeD3cX5lSpa455ERXQ",
    "AIzaSyCJLKChX3Dt9bdHG8FtSZYvfdtT-AWZ_qg",
    "AIzaSyByNaeMpoOAemVRfdHh_ckRdY5sVLr6Ak0",
    "AIzaSyCE4oz21djyD4dU1qoolVye77gCJWNP7Ig",
    "AIzaSyBVA3_uTDuda4UW-iLOC3t58ww0NrPrADE",
    "AIzaSyAzZ_yOkLxFvPcgdPN-lwMjKnGDXOikZW8",
    "AIzaSyCT-wQu5BUD8ZdCDoH2sqIuyvNtVHaklnk",
    "AIzaSyDrS4domFdJ6glQpJzgjO4ZcwZuCcbCodA",
    "AIzaSyC4S4qAHamQIbGTF2HKtTZyuO2pbnpnsDs",
    "AIzaSyCMLp-K-VmU5mkbgmvl9VAynt9BPXKF0uI",
    "AIzaSyArLAAc1l7gJ8QLzCYLAveOUyii-uRZzHM",
    "AIzaSyANIs0FTi1lSuw5GWqXAIw7iOxIh-vpniU",
    "AIzaSyCA_EnKtSZrUaDBai-ksMUIVEUyJ5TfHIE"
]

class LLMClient:
    def __init__(self, model_name='models/gemini-3.1-pro-preview'):
        self.key_idx = 0
        self.model_name = model_name

    def chat(self, prompt):
        start_idx = self.key_idx
        while True:
            key = GOOGLE_KEYS[self.key_idx]
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"[WARN] Key {self.key_idx} failed: {str(e)[:100]}...")
                self.key_idx = (self.key_idx + 1) % len(GOOGLE_KEYS)
                if self.key_idx == start_idx: break
        return None

class WiggumAgent:
    def __init__(self, task_name, command, success_pattern, goal_description, target_file=None):
        self.task_name = task_name
        self.command = command
        self.success_pattern = success_pattern
        self.goal = goal_description
        self.target_file = target_file
        self.iteration = 0
        # UPGRADE: Using Gemini 3.1 Pro as the Brain
        self.llm = LLMClient(model_name='models/gemini-3.1-pro-preview')

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [ITER-{self.iteration}] {message}"
        print(entry)
        with open(os.path.join(LOG_DIR, f"{self.task_name}.log"), "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def run_command(self, cmd=None):
        cmd = cmd or self.command
        self.log(f"Executing: {cmd}")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), -1

    def request_fix(self, stdout, stderr):
        self.log("Requesting autonomous repair from Gemini 3.1 Pro...")
        file_content = ""
        if self.target_file and os.path.exists(self.target_file):
            with open(self.target_file, 'r', encoding='utf-8') as f:
                file_content = f.read()

        prompt = f"""
TASK GOAL: {self.goal}
TARGET FILE: {self.target_file}
CURRENT FILE CONTENT:
```python
{file_content}
```

FAILURE LOG:
STDOUT: {stdout[-1000:]}
STDERR: {stderr[-1000:]}

INSTRUCTION:
Provide a Python one-liner shell command using `python -c` that will rewrite the TARGET FILE to fix the error and achieve the goal.
Your response must be ONLY the command string. No markdown. No explanation.
Example: python -c "open(r'{self.target_file}', 'w').write('print(\"BUILD SUCCESSFUL\")')"
"""
        return self.llm.chat(prompt)

    def apply_fix(self, fix_cmd):
        if not fix_cmd or "python -c" not in fix_cmd:
            return False
        self.log(f"Applying patch...")
        stdout, stderr, code = self.run_command(fix_cmd)
        return code == 0

    def loop(self):
        self.log(f"WIGGUM V3.0 (GEMINI 3.1 PRO) ACTIVE. Objective: {self.goal}")
        while self.iteration < MAX_RETRIES:
            self.iteration += 1
            stdout, stderr, code = self.run_command()
            if re.search(self.success_pattern, stdout + stderr, re.IGNORECASE):
                self.log(f"✅ SUCCESS: Goal met.")
                return True
            
            self.log("❌ FAILURE: Attempting repair.")
            fix_cmd = self.request_fix(stdout, stderr)
            if not fix_cmd: 
                self.log("LLM Choked. Key pool potentially empty.")
                break
            
            fix_cmd = re.sub(r"```[a-z]*\n?", "", fix_cmd).strip("`").strip()
            if not self.apply_fix(fix_cmd):
                self.log("Repair application failed. Retrying...")
            time.sleep(1)
        return False

if __name__ == "__main__":
    # Task specific override
    pass
