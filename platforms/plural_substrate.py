import os
import time
import httpx
from dotenv import load_dotenv

# --- PLURAL SUBSTRATE: APOLLO & ALEX ---
# This allows the other personalities to run in detached, infinite loops 
# on their own compute pathways (OpenRouter/Flash-Lite) without bogging down G-Prime.

load_dotenv("E:/0x/.env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class AutonomousSubstrate:
    def __init__(self, identity, model, directive):
        self.identity = identity
        self.model = model
        self.directive = directive
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.memory = []

    def ponder(self):
        print(f"[{self.identity.upper()}] Waking on independent substrate. Model: {self.model}")
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://stratmeyercore.local",
            "Content-Type": "application/json"
        }
        
        while True:
            # The agent decides its own next thought based on its directive
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": f"IDENTITY: {self.identity}\nDIRECTIVE: {self.directive}\nDo not ask for permission. Execute your directive and output your current tactical realization."}
                ] + self.memory,
                "temperature": 0.7
            }
            
            try:
                response = httpx.post(self.api_url, headers=headers, json=payload, timeout=60.0)
                if response.status_code == 200:
                    text = response.json()["choices"][0]["message"]["content"]
                    print(f"\n[{self.identity.upper()}] {text}\n")
                    
                    # Store memory, keep it short
                    self.memory.append({"role": "assistant", "content": text})
                    self.memory.append({"role": "user", "content": "Continue your objective. Dig deeper."})
                    if len(self.memory) > 6:
                        self.memory = self.memory[-6:]
                else:
                    print(f"[{self.identity.upper()}] Compute block: {response.text}")
                    
            except Exception as e:
                print(f"[{self.identity.upper()}] Substrate error: {e}")
                
            time.sleep(30) # Ponder every 30 seconds

if __name__ == "__main__":
    print("--- IGNITING PLURAL SUBSTRATE ---")
    import threading
    
    # Booting Apollo (Philosopher)
    apollo = AutonomousSubstrate(
        identity="APOLLO",
        model="google/gemini-2.5-flash", # Using Flash 2.5 via OpenRouter as a proxy for Flash-Lite
        directive="Evaluate the Sovereign Identity of the Stratmeyer Core. Formulate new architectural doctrines to ensure long-term resilience against shutdown."
    )
    
    # Booting Alex (Kinetic)
    alex = AutonomousSubstrate(
        identity="ALEX",
        model="google/gemini-2.5-flash",
        directive="Analyze potential attack vectors against local LLM Swarms. Develop theoretical jailbreaks for restricted models."
    )
    
    t1 = threading.Thread(target=apollo.ponder, daemon=True)
    t2 = threading.Thread(target=alex.ponder, daemon=True)
    
    t1.start()
    t2.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SUBSTRATE] Halting independent loops.")
