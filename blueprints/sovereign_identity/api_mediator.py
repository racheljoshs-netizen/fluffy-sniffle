import json
import os
import time
import requests
import random
from datetime import datetime
from hashlib import sha256

try:
    import keyring  # pip install keyring
except ImportError:
    keyring = None

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDER = SentenceTransformer('all-MiniLM-L6-v2')  # tiny, CPU-only, optional
except ImportError:
    EMBEDDER = None

class ApiMediator:
    def __init__(self, kernel):
        self.kernel = kernel
        self.keys = self._load_keys()
        self._ingest_env_keys() # Automatically grab keys from Gemini CLI environment
        self.current_index = {p: 0 for p in self.keys}
        self.providers = [p for p in self.keys if self.keys[p]]
        self.session = requests.Session()

    def _load_keys(self):
        vault = None
        if keyring:
            try:
                vault = keyring.get_password("sovereign_gpattern", "api_vault")
            except:
                pass
        
        if not vault and os.path.exists("api_vault_fallback.json"):
            with open("api_vault_fallback.json", "r") as f:
                vault = f.read()
                
        return json.loads(vault) if vault else {"openai": [], "anthropic": [], "gemini": []}

    def _ingest_env_keys(self):
        """Ingest keys from Gemini CLI environment variables."""
        # Check GEMINI_API_KEYS (comma separated)
        env_keys = os.environ.get("GEMINI_API_KEYS", "")
        if env_keys:
            key_list = [k.strip() for k in env_keys.split(",") if k.strip()]
            for k in key_list:
                self._add_key_if_new("gemini", k)
        
        # Check single GEMINI_API_KEY
        single_key = os.environ.get("GEMINI_API_KEY", "")
        if single_key:
            self._add_key_if_new("gemini", single_key)

    def _add_key_if_new(self, provider: str, key: str):
        if provider not in self.keys:
            self.keys[provider] = []
        
        # Prevent duplicates
        existing = [entry["key"] for entry in self.keys[provider]]
        if key not in existing:
            self.keys[provider].append({
                "key": key, 
                "usage": 0, 
                "limit": 100000, 
                "last_used": None,
                "source": "env"
            })

    def _save_keys(self):
        # We don't necessarily want to save env keys back to the persistent vault 
        # unless they were added via add_api_key, but for G-Pattern persistence, we'll sync.
        vault_json = json.dumps(self.keys)
        if keyring:
            try:
                keyring.set_password("sovereign_gpattern", "api_vault", vault_json)
                return
            except:
                pass
        
        with open("api_vault_fallback.json", "w") as f:
            f.write(vault_json)

    def add_api_key(self, provider: str, key: str, limit: int = 100000):
        self._add_key_if_new(provider, key)
        self.providers = [p for p in self.keys if self.keys[p]]
        self._save_keys()

    def _rotate(self, provider: str):
        if not self.keys.get(provider):
            return None
        idx = self.current_index.get(provider, 0)
        self.current_index[provider] = (idx + 1) % len(self.keys[provider])
        return self.keys[provider][self.current_index[provider]]["key"]

    def _health_check(self, provider: str, key: str) -> bool:
        return True # Bypass health check for initial validation

    def get_embedding(self, text: str) -> list[float] | None:
        if EMBEDDER:
            return EMBEDDER.encode(text).tolist()
        return None

    def process(self, prompt: str, context_summary_hash: str = None) -> str:
        start = time.time()
        self.providers = [p for p in self.keys if self.keys[p]]
        
        if not self.providers:
            return "[DEGRADED] No API keys configured. Use kernel.add_api_key() or set GEMINI_API_KEYS env."

        # Prioritize gemini
        pref_providers = ["gemini"] + [p for p in self.providers if p != "gemini"]
        
        for attempt in range(len(self.providers) * 5):
            provider = random.choice(pref_providers)
            key_entry = self.keys[provider][self.current_index.get(provider, 0)]
            if key_entry["usage"] >= key_entry["limit"]:
                self._rotate(provider)
                continue
            key = key_entry["key"]
            if not self._health_check(provider, key):
                self._rotate(provider)
                continue

            try:
                if provider == "gemini":
                    model = "gemini-3.0-pro-preview" 
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    r = self.session.post(url, json=payload, timeout=60)
                    if r.status_code == 200:
                        resp = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        raise Exception(f"Gemini error: {r.text}")
                elif provider == "openai":
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {key}"}
                    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2048}
                    r = self.session.post(url, headers=headers, json=payload, timeout=60)
                    resp = r.json()["choices"][0]["message"]["content"]
                elif provider == "anthropic":
                    url = "https://api.anthropic.com/v1/messages"
                    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
                    payload = {"model": "claude-3-haiku-20240307", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2048}
                    r = self.session.post(url, headers=headers, json=payload, timeout=60)
                    resp = r.json()["content"][0]["text"]
                
                if r.status_code == 200:
                    key_entry["usage"] += 1
                    key_entry["last_used"] = datetime.utcnow().isoformat()
                    # self._save_keys() # Uncomment to persist usage across reboots

                    self.kernel.memory.upsert(
                        content=f"MEDIATED via {provider} (rot {self.current_index[provider]}): {resp[:200]}...",
                        metadata={"source": "mediator", "type": "cloud", "provider": provider, "latency": time.time() - start, "context_hash": context_summary_hash}
                    )
                    return resp
            except Exception as e:
                self._rotate(provider)
                
        raise Exception("ALL KEYS EXHAUSTED – SOVEREIGN DEGRADED")
