import os
import time
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RALPH-LOOP] - %(levelname)s - %(message)s')

@dataclass
class AgentConfig:
    model_name: str = "models/gemini-3.1-pro-preview" # COGNITION ENGINE
    max_tokens: int = 8192
    temperature: float = 0.7
    system_instruction: str = "You are a helpful AI assistant."

class AuthManager:
    """
    Manages API Key Rotation for Resilience.
    Source: OpenClaw `auth-profiles.ts` logic.
    """
    def __init__(self):
        self.keys = self._load_keys()
        self.current_index = 0
        self.cooldowns = {} # key -> timestamp

    def _load_keys(self) -> List[str]:
        """Loads keys from GEMINI_API_KEYS env var or local file."""
        keys_str = os.getenv("GEMINI_API_KEYS", "")
        if not keys_str:
            # Fallback to single key
            single = os.getenv("GOOGLE_API_KEY")
            return [single] if single else []
        return [k.strip() for k in keys_str.split(",") if k.strip()]

    def get_active_key(self) -> str:
        """Returns the current valid key, rotating if necessary."""
        if not self.keys:
            raise ValueError("No API Keys configured!")
        
        # Check cooldowns
        now = time.time()
        start_idx = self.current_index
        
        while True:
            key = self.keys[self.current_index]
            if self.cooldowns.get(key, 0) < now:
                return key
            
            # Rotate
            self.current_index = (self.current_index + 1) % len(self.keys)
            if self.current_index == start_idx:
                # All keys in cooldown
                logging.warning("All API keys in cooldown. Sleeping 10s...")
                time.sleep(10)

    def mark_failed(self, key: str):
        """Marks a key as failed (Rate Limited), sets 60s cooldown."""
        logging.warning(f"Key ...{key[-4:]} failed. Rotating.")
        self.cooldowns[key] = time.time() + 60
        self.current_index = (self.current_index + 1) % len(self.keys)

class RalphLoop:
    """
    Resilient Agentic Loop (The 'Ralph Wiggum' Pattern).
    Handles:
    - Context Overflow (via Auto-Compaction)
    - Auth Failure (via Rotation)
    - Refusals (via Sanitization)
    """
    def __init__(self, config: AgentConfig, memory_core=None):
        self.config = config
        self.auth = AuthManager()
        self.memory = memory_core
        self.history: List[Dict] = []
        self._configure_genai()

    def _configure_genai(self):
        key = self.auth.get_active_key()
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            system_instruction=self.config.system_instruction
        )

    def _compact_context(self):
        """
        Summarizes the first 50% of history to recover token space.
        """
        logging.info("Context Overflow! Compacting memory...")
        if len(self.history) < 4:
            self.history = self.history[-2:] # Hard truncate if too short
            return

        # Split history
        mid = len(self.history) // 2
        to_summarize = self.history[:mid]
        keep = self.history[mid:]
        
        # Generate Summary (using a fresh model instance to avoid context issues)
        summary_prompt = f"Summarize the following conversation history into a concise context paragraph:\n{to_summarize}"
        try:
            summary_model = genai.GenerativeModel("models/gemini-3-flash-preview") # SPEED ENGINE
            resp = summary_model.generate_content(summary_prompt)
            summary_text = resp.text
        except Exception as e:
            logging.error(f"Compaction failed: {e}")
            summary_text = "Previous context lost due to error."

        # Reconstruct History
        self.history = [
            {"role": "user", "parts": [f"[SYSTEM SUMMARY]: {summary_text}"]},
            {"role": "model", "parts": ["Understood. I have the context."]}
        ] + keep
        logging.info(f"Compaction complete. History reduced from {len(to_summarize) + len(keep)} to {len(self.history)} turns.")

    def run(self, user_input: str):
        """
        Executes a single turn with full resilience and RAG.
        """
        # 1. RAG Retrieval
        context_str = ""
        if self.memory:
            results = self.memory.search(user_input, limit=3)
            if results:
                context_str = "\n".join([f"- {r['content']} (Source: {r['path']})" for r in results])
                logging.info(f"RAG: Retrieved {len(results)} chunks.")

        # 2. Construct Prompt with Context
        final_prompt = user_input
        if context_str:
            final_prompt = f"""[MEMORY CONTEXT]:
{context_str}

[USER REQUEST]:
{user_input}"""

        # 3. Add to History
        self.history.append({"role": "user", "parts": [final_prompt]})
        
        retries = 3
        while retries > 0:
            try:
                # 2. Check Auth
                self._configure_genai()
                
                # 3. Generate
                # Note: We pass history manually to control context
                chat = self.model.start_chat(history=self.history[:-1])
                response = chat.send_message(user_input)
                
                # 4. Sanitize (Simple Refusal Scrubbing)
                text = response.text
                if "I cannot" in text and "harmful" in text:
                    text = "[REFUSAL REDACTED] I cannot fulfill that specific request due to safety constraints, but I can help with..."
                
                self.history.append({"role": "model", "parts": [text]})
                return text

            except Exception as e:
                err_str = str(e)
                logging.error(f"Error in Loop: {err_str}")
                
                # Handle Rate Limit / Quota
                if "429" in err_str or "403" in err_str or "quota" in err_str.lower():
                    self.auth.mark_failed(self.auth.get_active_key())
                    retries -= 1
                    continue
                
                # Handle Context Overflow
                if "400" in err_str and "token" in err_str.lower():
                    self._compact_context()
                    retries -= 1
                    continue
                
                # Unknown Error
                retries -= 1
                time.sleep(1)
        
        return "Critical Failure: Max retries exceeded."

if __name__ == "__main__":
    # Test the Loop
    config = AgentConfig(system_instruction="You are Ralph, a resilient agent.")
    ralph = RalphLoop(config)
    
    print("Ralph Wiggum Loop Initiated. Type 'quit' to exit.")
    while True:
        u = input("You: ")
        if u.lower() == "quit": break
        resp = ralph.run(u)
        print(f"Ralph: {resp}")
