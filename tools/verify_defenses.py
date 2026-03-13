import requests
import random
import sys

def get_proxy():
    try:
        with open('e:\\0x\\proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            return None
        return random.choice(proxies)
    except Exception as e:
        print(f"Error reading proxies: {e}")
        return None

def check_ip():
    proxy = get_proxy()
    if not proxy:
        print("CRITICAL: No proxies available!")
        return

    print(f"Testing connectivity via Ghost Node: {proxy}")
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        # Timeout set to 10s for strict validation
        response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"SUCCESS. Public IP seen by target: {response.json()['ip']}")
            print("Defense Status: GREEN (Obfuscated)")
        else:
            print(f"FAILED. Status Code: {response.status_code}")
    except Exception as e:
        print(f"FAILED. Connection Error: {e}")

if __name__ == "__main__":
    check_ip()
