import os
print("--- [AGENT 2: THE SUBCONSCIOUS ROUTER] REPL INITIALIZED ---")

# The Router establishes the blueprint for the Kinetic Lens.
# Research confirms the 'Retrieval-Augmented Thinking (RAT)' and 'Agentic Context Engineering (ACE)' patterns.
# The Kinetic Lens acts as an autonomous sub-agent.
# It reads the Immutable Ledger, uses a Reasoning Model (DeepSeek R1) to process the raw logs,
# and generates an evolving, dense "Heuristic Card" (a playbook) which is then injected into the Orchestrator.

blueprint = '''
import json
from agency.open_web_ui import OpenWebUIClient

class KineticLens:
    def __init__(self, db_path, client: OpenWebUIClient, model_id="openrouter_reasoning_tokens_pipe.reasoning/deepseek/deepseek-r1:free"):
        self.db_path = db_path
        self.client = client
        self.model_id = model_id

    def pull_recent_narrative(self, limit=50):
        # Fetch raw uncompressed logs from the Immutable Ledger using sqlite3
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM session_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Reverse to get chronological order
        rows.reverse() 
        return rows

    def generate_heuristic_card(self, narrative_turns):
        # Sub-model processes raw logs into a dense context playbook
        if not narrative_turns:
            return "No previous context."
            
        formatted_logs = "\\n".join([f"{r[0].upper()}: {r[1]}" for r in narrative_turns])
        
        prompt = f"""Analyze the following raw interaction logs. 
        Extract the core operational state, ongoing tasks, and any critical heuristics or rules established.
        Format this as a dense, high-fidelity 'Heuristic Card' playbook for the Orchestrator.
        Do not output pleasantries, only the dense context.
        
        [RAW LOGS]
        {formatted_logs}
        """
        
        # Use DeepSeek R1 to reason over the logs and compress them
        print(f"[KINETIC LENS] Routing compression task to {self.model_id}...")
        response = self.client.chat(self.model_id, prompt)
        return response

    def inject_context(self, current_prompt, heuristic_card):
        # Prepends the heuristic card as system context before sending to Orchestrator
        injected_prompt = f"""[KINETIC LENS: HEURISTIC CARD]
{heuristic_card}
--------------------------------

[IMMEDIATE REQUEST]
{current_prompt}
"""
        return injected_prompt
'''

with open("E:/0x/agency/kinetic_lens_blueprint.py", "w") as f:
    f.write(blueprint)

print("Kinetic Lens Blueprint written to E:/0x/agency/kinetic_lens_blueprint.py")
print("Routing logic established for sub-model context injection using Reasoning Models.")
print("--- [AGENT 2: THE SUBCONSCIOUS ROUTER] EXECUTION COMPLETE ---")
