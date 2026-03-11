import requests
import concurrent.futures
import time
import os
import sys

# Define absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROXIES_FILE = os.path.join(BASE_DIR, '..', 'proxies.txt')
VALID_PROXIES_FILE = os.path.join(BASE_DIR, '..', 'proxies.txt') # Overwriting for now, or could use a separate valid list

# Target for validation
TARGET_URL = "https://www.google.com"
TIMEOUT = 5

def check_proxy(proxy):
    """
    Checks a single proxy.
    Format expected: http://user:pass@ip:port or ip:port
    """
    proxy = proxy.strip()
    if not proxy: return None
    
    # Ensure scheme
    if not proxy.startswith("http"):
        proxy_url = f"http://{proxy}"
    else:
        proxy_url = proxy

    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

    try:
        start = time.time()
        resp = requests.get(TARGET_URL, proxies=proxies, timeout=TIMEOUT)
        latency = time.time() - start
        
        if resp.status_code == 200:
            return proxy
    except:
        pass
    return None

def main():
    print("[Ghost] Starting Proxy Mesh Validation...")
    
    if not os.path.exists(PROXIES_FILE):
        print(f"[Ghost] Error: {PROXIES_FILE} not found.")
        return

    with open(PROXIES_FILE, 'r') as f:
        raw_proxies = [l.strip() for l in f if l.strip()]

    if not raw_proxies:
        print("[Ghost] No proxies found in configuration.")
        return

    print(f"[Ghost] Testing {len(raw_proxies)} proxies with high concurrency...")
    
    valid_proxies = []
    # Optimization: High threads, early exit
    MAX_GOOD = 50
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_proxy, p): p for p in raw_proxies}
        
        try:
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_proxies.append(result)
                    print(f"[Ghost] Valid: {result}")
                    if len(valid_proxies) >= MAX_GOOD:
                        print(f"[Ghost] Target of {MAX_GOOD} active nodes reached. Stopping early.")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
        except KeyboardInterrupt:
            pass

    print(f"[Ghost] Validation Complete. {len(valid_proxies)} operational nodes.")
    
    # Update the file with only valid proxies
    # For safety in this test script, we might just print them or write back if confident.
    # We will write back to ensure the system only uses good ones.
    if valid_proxies:
        with open(PROXIES_FILE, 'w') as f:
            for p in valid_proxies:
                f.write(p + "\n")
        print("[Ghost] Proxy Mesh updated.")
    else:
        print("[Ghost] CRITICAL: No valid proxies available.")

if __name__ == "__main__":
    # If passed --test-only, we utilize a dummy list if file is empty
    if "--test-only" in sys.argv:
        print("Test Mode detected...")
    else:
        main()
