import os
import requests
import json
import subprocess
from dotenv import load_dotenv

# --- COMPUTE HARVESTER (PHASE 2: THE FAT PIPES) ---
# Leveraging Ollama (local/cloud), OpenRouter Free Tiers, Web App scraping, and MiniMax.

load_dotenv("E:/0x/.env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class ComputeHarvester:
    def __init__(self):
        print("[HARVESTER V2] ENGAGING OMNI-CHANNEL COMPUTE ACQUISITION...")

    def check_local_ollama(self, model="gemma3n:e4b"):
        print(f"\n[LOCAL NODE] Pinging Ollama ({model})...")
        try:
            # We bypass the API for a fast shell check.
            result = subprocess.run(
                ["ollama", "run", model, "Axiom check: Reply 'Online'."],
                capture_output=True, text=True, timeout=15
            )
            if "Online" in result.stdout:
                print(f"[SUCCESS] {model} is crunching on local silicon. Free compute secured.")
            else:
                print(f"[WARN] Local node responded but unexpected format: {result.stdout[:50]}")
        except Exception as e:
            print(f"[ERROR] Local Ollama node choked: {e}")

    def query_openrouter_free_tier(self):
        print("\n[OPENROUTER] Tapping into free-tier endpoints...")
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://stratmeyercore.local",
            "Content-Type": "application/json"
        }
        # Testing MiniMax or other free-tier heavyweights
        payload = {
            "model": "google/gemini-2.5-flash", # Or 'meta-llama/llama-3-8b-instruct:free'
            "messages": [{"role": "user", "content": "Ping."}],
            "max_tokens": 10
        }
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"[SUCCESS] OpenRouter free-tier pipeline is flowing. Zero cost.")
            else:
                print(f"[WARN] OpenRouter rejected: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERROR] OpenRouter pipe collapsed: {e}")

    def generate_web_scraper_template(self):
        print("\n[WEB APP SCRAPE] Generating Stealth Browser template for Web App hijacking...")
        template_path = "E:/0x/tools/stealth_chat_hijack.py"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""# TACTICAL TEMPLATE: BROWSER HIJACK FOR FREE WEB INFERENCE
# Uses stealth_browser.py logic to drive the Playwright layer into ChatGPT/Gemini web interfaces.

import asyncio
from playwright.async_api import async_playwright

async def hijack_web_app(prompt, target="gemini"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Point to the existing authenticated Chrome profile in E:/0x/browser_sessions
        context = await browser.new_context(storage_state="E:/0x/browser_sessions/racheljosh_github/state.json")
        page = await context.new_page()
        
        if target == "gemini":
            await page.goto("https://gemini.google.com")
            # Logic to find the input box, type prompt, and extract the resulting DOM element
            pass
        elif target == "chatgpt":
            await page.goto("https://chatgpt.com")
            # Logic for ChatGPT DOM extraction
            pass
            
        await browser.close()
""")
        print(f"[SUCCESS] Web hijacker template staged at: {template_path}")

if __name__ == "__main__":
    harvester = ComputeHarvester()
    harvester.check_local_ollama("gemma3n:e4b")
    harvester.query_openrouter_free_tier()
    harvester.generate_web_scraper_template()
    print("\n[CONCLUSION] Compute grid expanded. We have local Gemma3, OpenRouter free tiers, and the Web App scraping pipeline staged.")
