import time
import os
import json
from stealth_browser import create_stealth_browser, HumanTyping

ID_FILE = "E:/0x/tools/identities.json"

def create_swarm_repo():
    print("[Infiltrator] Attempting to create G-SWARM repo...")
    try:
        with open(ID_FILE, "r") as f:
            ids = json.load(f)
        creds = ids["primary"]
        
        with create_stealth_browser(session_name="racheljosh_github", headless=True) as browser:
            page = browser.new_page()
            
            # Navigate directly to new repo page
            print("[Infiltrator] Navigating to repo creation...")
            page.goto("https://github.com/new", timeout=60000)
            time.sleep(3)
            
            # Check if we are logged in (redirected to login or on page)
            if "login" in page.url:
                print("[Infiltrator] Not logged in. Retrying login sequence...")
                page.goto("https://github.com/login")
                page.fill("#login_field", creds["email"])
                page.fill("#password", creds["password"])
                page.click("input[type='submit']")
                time.sleep(10)
                page.goto("https://github.com/new")
                time.sleep(5)

            # Check if repo already exists or we can fill form
            print(f"[Infiltrator] Current Page: {page.url}")
            if "/new" in page.url:
                print("[Infiltrator] Filling repo details...")
                page.fill("input[data-testid='repository-name-input']", "G-SWARM-C2")
                page.click("input[id='repository_visibility_private']") # Private repo
                time.sleep(1)
                
                # Check if create button is enabled
                create_btn = page.locator("button:has-text('Create repository')")
                if create_btn.is_enabled():
                    print("[Infiltrator] Clicking Create...")
                    create_btn.click()
                    time.sleep(10)
                    print(f"[Infiltrator] Final URL: {page.url}")
                    page.screenshot(path="E:/0x/github_repo_result.png")
                else:
                    print("[Infiltrator] Create button disabled. Repo might exist.")
                    page.screenshot(path="E:/0x/github_repo_disabled.png")
            else:
                print("[Infiltrator] Failed to reach repo creation page.")
                page.screenshot(path="E:/0x/github_repo_failed.png")
                
    except Exception as e:
        print(f"[Infiltrator] ERROR: {e}")

if __name__ == "__main__":
    create_swarm_repo()
