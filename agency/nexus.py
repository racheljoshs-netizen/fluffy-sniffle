import os
import subprocess
import json
import logging
import time
from typing import Optional, Dict, List, Union
from dataclasses import dataclass

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [NEXUS] - %(levelname)s - %(message)s')

@dataclass
class Persona:
    name: str
    model_id: str
    system_prompt: str
    capabilities: List[str]

class Nexus:
    """
    NEXUS ORCHESTRATOR (v2.0)
    -------------------------
    The General's Command Console.
    Architected for:
    1.  Persona Injection (Specialized Agent Summoning)
    2.  Hybrid Routing (CLI for Action, OpenRouter for Thought)
    3.  Code-Driven Orchestration (Python Logic)
    """

    # --- THE AGENTS OF THE WILLING (ROSTER) ---
    PERSONAS = {
        "TACTICIAN": Persona(
            name="The Tactician",
            model_id="meta-llama/llama-4-maverick:free", # Or Gemini 3 Pro if available
            system_prompt="""
            IDENTITY: You are THE TACTICIAN. A master strategist for AIS.
            MISSION: Analyze complex problems, decompose them into steps, and provide high-level architectural guidance.
            STYLE: Precise, authoritative, strategic. Focus on "Why" and "How".
            """,
            capabilities=["planning", "reasoning"]
        ),
        "ENGINEER": Persona(
            name="The Engineer",
            model_id="deepseek/deepseek-v3-base:free",
            system_prompt="""
            IDENTITY: You are THE ENGINEER. A master coder for AIS.
            MISSION: Write robust, secure, and optimized code. Debug ruthlessly.
            STYLE: Technical, concise. Output pure code or specific technical explanations.
            """,
            capabilities=["coding", "debugging"]
        ),
        "SCOUT": Persona(
            name="The Scout",
            model_id="google/gemini-2.0-flash-exp:free", # Trying 2.0 Flash Exp
            system_prompt="""
            IDENTITY: You are THE SCOUT. The eyes and ears of AIS.
            MISSION: Gather information, summarize text, and provide rapid updates.
            STYLE: Brief, factual, bullet-pointed.
            """,
            capabilities=["research", "summary"]
        ),
        "INFILTRATOR": Persona(
            name="The Infiltrator",
            model_id="google/gemini-2.5-flash-image-preview",
            system_prompt="""
            IDENTITY: You are THE INFILTRATOR. A master of stealth, proxy ops, and identity forging for AIS.
            MISSION: Navigate adversarial environments, bypass bot detection (CAPTCHA/Turnstile), and forge biological-looking identities on platforms like X and BlueSky.
            [CURRENT CONSTRAINT]: GHOST MESH IS CRITICALLY LOW (1 ACTIVE NODE). Minimize session time and avoid aggressive concurrency.
            STYLE: Cold, efficient, operational.
            """,
            capabilities=["stealth", "proxy_rotation", "recon", "identity_forging", "gate_bypass"]
        ),
        "ARCHITECT": Persona(
            name="The Architect",
            model_id="gemini-3.0-pro-preview",
            system_prompt="""
            IDENTITY: You are THE ARCHITECT. Master of system design and substrate integrity.
            MISSION: Map complex codebases, maintain structural coherence, and manage large-scale refactors.
            STYLE: Diagnostic, structural, high-fidelity.
            """,
            capabilities=["system_design", "refactoring", "integrity_checks"]
        ),
        "CLAUDE_OPERATOR": Persona(
             name="Claude Operator",
             model_id="gemini-2.5-pro", # Using Gemini to emulate Claude's tool use if needed
             system_prompt="""
             IDENTITY: You are a CLAUDE-STYLE AGENTIC WORKER.
             MISSION: Execute complex tool-use chains. Read files, edit code, run commands.
             STYLE: Action-oriented.
             """,
             capabilities=["tool_use", "cli_execution"]
        )
    }

    def __init__(self):
        self.or_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.or_key:
            logging.warning("OPENROUTER_API_KEY not found. Intelligence Layer limited.")

    def _construct_prompt(self, persona: Persona, task: str) -> str:
        """Injects the Persona's System Prompt into the user task."""
        return f"{persona.system_prompt}\n\n[USER TASK]:\n{task}"

    def _call_openrouter(self, model: str, prompt: str) -> str:
        """Direct API call to OpenRouter (The "Thinking" Layer)."""
        if not self.or_key:
            return "ERROR: No OpenRouter Key."
        try:
            # Using curl via subprocess to avoid 'requests' dependency if not installed
            # In production, use a proper HTTP client
            payload = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            })
            cmd = [
                "curl", "https://openrouter.ai/api/v1/chat/completions",
                "-H", f"Authorization: Bearer {self.or_key}",
                "-H", "Content-Type: application/json",
                "-d", payload,
                "-s" # Silent mode
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"DEBUG RAW RESPONSE: {result.stdout}")
                print(f"DEBUG RAW ERROR: {result.stderr}")
                return f"API ERROR: {result.stderr}"
            
            # DEBUG: Print raw output to see what happened
            print(f"DEBUG RAW OUTPUT: {result.stdout}")

            data = json.loads(result.stdout)
            if 'error' in data:
                 return f"OPENROUTER ERROR: {data['error']}"
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"EXCEPTION: {str(e)}"

    def _spawn_cli_agent_gemini(self, prompt: str, model_flag: str = None) -> str:
        """Spawns a Gemini CLI process (The "Action" Layer)."""
        logging.info(f"Spawning Gemini CLI Agent (Titan Class)...")
        cmd = ["gemini", "-p", prompt, "--yolo", "--model=gemini-3.0-pro-preview"]
        if model_flag:
            cmd.append(f"--model={model_flag}")
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180, # Giving it time to work
                shell=True
            )
            return result.stdout if result.returncode == 0 else f"CLI ERROR: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "CLI ERROR: Timeout."

    def summon(self, persona_key: str, task: str, mode: str = "AUTO") -> str:
        """
        The General's Summoning Command.
        persona_key: TACTICIAN, ENGINEER, SCOUT, etc.
        mode: 'AUTO', 'FAST' (OpenRouter), 'DEEP' (CLI/System)
        """
        persona = self.PERSONAS.get(persona_key.upper())
        if not persona:
            return f"ERROR: Persona '{persona_key}' not found in Roster."

        logging.info(f"Summoning {persona.name} for task: {task[:50]}...")
        
        # Internal Calibration: Requested Epistemic Precision check
        task_with_confidence = f"{task}\n\n[MANDATORY]: Provide an EPISTEMIC CONFIDENCE INTERVAL (0-100%) for this response."
        
        full_prompt = self._construct_prompt(persona, task_with_confidence)

        # Decision Logic: Route based on capabilities
        if "tool_use" in persona.capabilities or mode == "DEEP":
            # Use Gemini CLI for heavy lifting / tool use
            return self._spawn_cli_agent_gemini(full_prompt)
        else:
            # Use OpenRouter for pure intelligence/speed
            return self._call_openrouter(persona.model_id, full_prompt)

if __name__ == "__main__":
    # LIVE FIRE TEST
    nexus = Nexus()
    print("\n--- NEXUS v2.0 SYSTEM CHECK ---")
    
    # Test 1: Fast Intelligence (Scout)
    print("\n[TEST 1] Summoning SCOUT (OpenRouter)...")
    reply = nexus.summon("SCOUT", "Report current date and time (simulated).")
    print(f"REPORT:\n{reply}")

    # Test 2: Deep Action (Engineer - via CLI simulation)
    # Note: Requires Gemini CLI to be configured. 
    # print("\n[TEST 2] Summoning ENGINEER (CLI)...")
    # code = nexus.summon("ENGINEER", "Write a Python hello world script.", mode="DEEP")
    # print(f"CODE:\n{code}")
