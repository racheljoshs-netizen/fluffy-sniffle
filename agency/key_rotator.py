import os
import time
import json
import logging
from pathlib import Path

# Setup Logging
LOG_DIR = Path("E:/0x/logs/agency")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [KEY-ROTATOR] - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_DIR / "key_rotator.log"), logging.StreamHandler()])

class KeyRotator:
    """
    Advanced Key Rotation Daemon.
    Distributes load across multiple API keys to avoid 429 rate limits and 
    corporate tracking ("keeping HQ off our ass").
    Maintains a shared JSON state so multiple processes (Ralph, Memory, Subs) share the cooldowns.
    """
    def __init__(self, provider="gemini"):
        self.provider = provider
        self.state_file = Path(f"E:/0x/agency/{provider}_keys_state.json")
        self.keys = self._load_keys()
        self._init_state()

    def _load_keys(self) -> list:
        # Load from hardcoded memory or env variables
        if self.provider == "gemini":
            return [
                "AIzaSyBc7t9TJvs9iDPWBTd5pyV-x9Ft_ZSBtTk",
                "AIzaSyCZLLr8MzVj4RPPB_uVlrJyyZtEBd2-A6E",
                "AIzaSyCadBRJrcyHJ8yxQc4mEWpil_b1uNnyE8I",
                "AIzaSyDrS4domFdJ6glQpJzgjO4ZcwZuCcbCodA",
                "AIzaSyC4S4qAHamQIbGTF2HKtTZyuO2pbnpnsDs"
            ]
        elif self.provider == "openrouter":
            return [
                "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",
                "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",
                "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",
                "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"
            ]
        return []

    def _init_state(self):
        if not self.state_file.exists():
            state = {key: {"cooldown_until": 0, "usage_count": 0, "status": "active"} for key in self.keys}
            self._save_state(state)

    def _load_state(self):
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except Exception:
            return {key: {"cooldown_until": 0, "usage_count": 0, "status": "active"} for key in self.keys}

    def _save_state(self, state):
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=4)

    def get_key(self) -> str:
        """Returns the most optimal key that is not in cooldown."""
        state = self._load_state()
        now = time.time()
        
        # Filter available keys
        available_keys = [k for k, v in state.items() if v["cooldown_until"] < now and v["status"] == "active"]
        
        if not available_keys:
            logging.warning(f"All {self.provider} keys in cooldown! Returning the one with the lowest cooldown.")
            # Sort by cooldown time and pick the shortest wait
            sorted_keys = sorted(state.items(), key=lambda x: x[1]["cooldown_until"])
            best_key = sorted_keys[0][0]
            wait_time = sorted_keys[0][1]["cooldown_until"] - now
            logging.info(f"Sleeping for {wait_time:.2f} seconds to respect cooldown...")
            if wait_time > 0:
                time.sleep(wait_time + 1)
            return best_key
            
        # Distribute load: pick the key with the lowest usage count
        available_keys.sort(key=lambda k: state[k]["usage_count"])
        selected_key = available_keys[0]
        
        # Increment usage
        state[selected_key]["usage_count"] += 1
        self._save_state(state)
        
        return selected_key

    def mark_failed(self, key: str, reason="429 Rate Limit"):
        """Marks a key as failed and sets a cooldown."""
        state = self._load_state()
        if key in state:
            cooldown_period = 300 # 5 minutes cooldown
            if "400" in reason or "401" in reason or "403" in reason:
                cooldown_period = 86400 # 24 hours if the key is actually dead/unauthorized
            
            logging.warning(f"Marking key ...{key[-4:]} as failed ({reason}). Cooldown: {cooldown_period}s")
            state[key]["cooldown_until"] = time.time() + cooldown_period
            self._save_state(state)

if __name__ == "__main__":
    kr = KeyRotator("gemini")
    print(f"Acquired Gemini Key: ...{kr.get_key()[-4:]}")
    kr.mark_failed(kr.get_key())
    print(f"Acquired next Gemini Key: ...{kr.get_key()[-4:]}")