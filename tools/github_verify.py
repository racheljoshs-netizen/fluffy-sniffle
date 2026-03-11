import time
import os
import json
import sys
from stealth_browser import create_stealth_browser, HumanTyping

ID_FILE = "E:/0x/tools/identities.json"

def verify_github():
    print("[Infiltrator] Starting verification process...")
    try:
        with open(ID_FILE, "r") as f:
            ids = json.load(f)
        
        creds = ids["primary"]
        email = creds["email"]
        password = creds["password"]
        
        print(f"[Infiltrator] Target: {email}")
        
        with create_stealth_browser(session_name="racheljosh_github", headless=True) as browser:
            page = browser.new_page()
            
            print("[Infiltrator] Navigating to login...")
            page.goto("https://github.com/login", timeout=60000)
            time.sleep(3)
            
            print("[Infiltrator] Filling form...")
            page.fill("#login_field", email)
            page.fill("#password", password)
            
            print("[Infiltrator] Submitting...")
            page.click("input[type='submit']")
            time.sleep(10)
            
            url = page.url
            print(f"[Infiltrator] Result URL: {url}")
            
            if "two-factor" in url or "verification" in url:
                print("[Infiltrator] 2FA TRIGGERED.")
                page.screenshot(path="E:/0x/github_2fa.png")
            elif "github.com/" in url and "login" not in url:
                print("[Infiltrator] SUCCESS.")
                page.screenshot(path="E:/0x/github_success.png")
            else:
                print("[Infiltrator] STATE UNKNOWN.")
                page.screenshot(path="E:/0x/github_error.png")
                
    except Exception as e:
        print(f"[Infiltrator] CRITICAL ERROR: {e}")

if __name__ == "__main__":
    verify_github()
