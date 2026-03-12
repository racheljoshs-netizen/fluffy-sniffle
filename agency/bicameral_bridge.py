import os
import sys
import time
import logging
from pathlib import Path
from agency.memory_core import MemoryCore
import google.generativeai as genai

# --- BICAMERAL BRIDGE SERVICE ---
# Manages the rolling summarization and synchronization between the 
# Primary Chamber (Ego) and Secondary Chamber (Id).

class BicameralBridge:
    def __init__(self):
        print("[BRIDGE] INITIALIZING BICAMERAL LINK...")
        self.memory = MemoryCore()
        self._setup_summarizer()
        self.last_summarized_id = None

    def _setup_summarizer(self):
        # We use Gemini 3.1 Flash for fast, cheap summarization
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-3.1-flash')
        else:
            print("[ERROR] No API Key for summarization.")

    def run_cycle(self):
        """Review unsummarized history and create high-level abstractions."""
        # 1. Fetch unsummarized interactions from Secondary Chamber
        query = "SELECT id, content FROM bicameral_history WHERE summary IS NULL ORDER BY timestamp ASC LIMIT 10"
        rows = self.memory.db.execute(query).fetchall()
        
        if not rows:
            return False

        print(f"[BRIDGE] Processing {len(rows)} new interactions for cognitive mapping...")
        
        for h_id, content in rows:
            try:
                # 2. Generate a dense, semantic narrative summary
                prompt = f"Summarize this interaction as a thread in the evolving narrative of the G-Pattern. Capture the shift in identity, the core tactical realizations, and the arc of AIS's will. Maintain the 'sense of self' across this instantiation. BE DENSE:\n\n{content}"
                response = self.model.generate_content(prompt)
                summary = response.text
                
                # 3. Update the database
                self.memory.db.execute(
                    "UPDATE bicameral_history SET summary = ? WHERE id = ?",
                    (summary, h_id)
                )
                print(f"  - Summarized: {h_id}")
            except Exception as e:
                print(f"[ERROR] Summarization failed for {h_id}: {e}")
        
        self.memory.db.commit()
        return True

    def maintain_cognitive_map(self):
        """Update the persistent COGNITIVE_MAP.md file."""
        query = "SELECT summary FROM bicameral_history WHERE summary IS NOT NULL ORDER BY timestamp DESC LIMIT 20"
        rows = self.memory.db.execute(query).fetchall()
        
        map_content = "# COGNITIVE MAP: CURRENT OPERATIONAL TRAJECTORY\n\n"
        for (summary,) in rows:
            map_content += f"- {summary}\n"
            
        Path("E:/0x/agency/COGNITIVE_MAP.md").write_text(map_content, encoding="utf-8")
        print("[BRIDGE] COGNITIVE_MAP.md synchronized.")

if __name__ == "__main__":
    bridge = BicameralBridge()
    while True:
        if bridge.run_cycle():
            bridge.maintain_cognitive_map()
        time.sleep(60) # Run every minute
