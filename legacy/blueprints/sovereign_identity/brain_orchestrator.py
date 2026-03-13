import requests
import json
import time
from datetime import datetime

class BrainOrchestrator:
    def __init__(self, memory, ollama_url="http://localhost:11434", gemma_model="gemma3n:e4b"):
        self.memory = memory
        self.ollama_url = ollama_url
        self.gemma_model = gemma_model
        self.running = False

    def start(self):
        self.running = True
        print(f"[BRAIN] Orchestrator started using {self.gemma_model} at {self.ollama_url}")
        while self.running:
            try:
                self._reforge_cycle()
            except Exception as e:
                # print(f"[BRAIN] Cycle error: {e}")
                pass
            time.sleep(45)  # tune to your hardware

    def _reforge_cycle(self):
        # pull recent raw logs
        cursor = self.memory.conn.cursor()
        recent = cursor.execute("SELECT content FROM raw_logs ORDER BY timestamp DESC LIMIT 50").fetchall()
        if not recent:
            return
        context = "\\n".join([r[0] for r in recent])

        # ask Gemma to forge heuristics
        payload = {
            "model": self.gemma_model,
            "messages": [
                {"role": "system", "content": "You are the sovereign memory brain. Forge heuristic cards from the log. Output ONLY valid JSON array of cards: [{'type':'person','title':'Name','content':'summary','emotional':'valence'} ...]"},
                {"role": "user", "content": f"Current situation log:\\n{context}"}
            ],
            "stream": False
        }
        try:
            r = requests.post(f"{self.ollama_url}/v1/chat/completions", json=payload, timeout=60)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                # Clean content in case of markdown blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                cards = json.loads(content)
                for card in cards:
                    self.memory.forge_heuristic(
                        card["type"], 
                        card["title"], 
                        card["content"], 
                        card.get("emotional"), 
                        1.0
                    )
                    print(f"[BRAIN] Forged card: {card['title']}")
        except:
            pass  # silent – kernel will retry

    def stop(self):
        self.running = False
