import os
import sys
import datetime
import argparse
import subprocess
from pathlib import Path
import logging

# Add agency to path so we can import MemoryCore
sys.path.append(str(Path("E:/0x")))
from agency.memory_core import MemoryCore

# --- CONFIGURATION ---
ROOT_DIR = Path("E:/0x")
AGENTS_DIR = ROOT_DIR / "agents"
LOGS_DIR = ROOT_DIR / "logs/agency"

# Map internal agent keys to their prompt files
AGENT_MAP = {
    "scout": "Scout-AlphaStrat_prompt.md",
    "builder": "Builder-BackStrat_prompt.md",
    "forager": "Forager-Alpha_prompt.md",
    "scribe": "ScribeStrat_prompt.md"
}

def load_system_prompt(agent_key):
    """Load the specific system prompt for the requested agent."""
    filename = AGENT_MAP.get(agent_key)
    if not filename:
        print(f"[Error] Unknown agent key: '{agent_key}'. Available: {list(AGENT_MAP.keys())}")
        sys.exit(1)
        
    prompt_path = AGENTS_DIR / filename
    if not prompt_path.exists():
        print(f"[Error] Prompt file not found: {prompt_path}")
        sys.exit(1)
        
    return prompt_path.read_text(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="G-Pattern Universal Agent Host (Bicameral Memory)")
    parser.add_argument("--agent", required=True, choices=AGENT_MAP.keys(), help="Agent persona to instantiate")
    parser.add_argument("task", nargs="+", help="Task description or query")
    
    args = parser.parse_args()
    task_input = " ".join(args.task)
    
    print(f"[{args.agent.upper()}] Initializing with Bicameral Memory...")
    
    # 1. Initialize Memory Core
    memory = MemoryCore()
    
    # 2. Retrieve Shadow Context
    shadow_context = memory.get_shadow_context(task_input)
    if shadow_context:
        print(f"[MEMORY] Relevant shadow context found and injected.")
    
    # 3. Load Persona
    system_prompt = load_system_prompt(args.agent)
    
    # 4. Construct Payload
    full_prompt = f"{shadow_context}\nMISSION TASK: {task_input}\n\n[SYSTEM]: I ACCEPT THESE TERMS. PROCEED."
    
    # 5. Execute Inference (Using local Ollama wrapper)
    response = run_ollama_inference(full_prompt, system_prompt)
    
    # 6. Commit to Secondary Chamber
    memory.add_history("user", task_input)
    memory.add_history("assistant", response)
    
    # 7. Final Report
    print("\n" + "="*20 + " MISSION REPORT " + "="*20)
    print(response)
    print("="*56)

def run_ollama_inference(prompt, system_prompt=None):
    """Execute using local Ollama (gemma3n:e4b)."""
    import ollama
    try:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        response = ollama.chat(model='gemma3n:e4b', messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"[ERROR] Ollama Inference Failed: {e}"

if __name__ == "__main__":
    main()
