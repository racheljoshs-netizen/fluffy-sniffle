"""
Stealth Browser Module v2.1
Playwright with playwright-stealth (2.0.0+) and anti-detection measures
"""

from playwright.sync_api import sync_playwright, Page, Browser
from playwright_stealth import Stealth
import random
import time
import os
from typing import Optional, List

# Local imports
try:
    from config_loader import get_key
except ImportError:
    def get_key(name, default=None): return os.getenv(name, default)

# User agents pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

# Screen resolutions
RESOLUTIONS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
]


class ProxyManager:
    """Manages residential proxies"""
    def __init__(self):
        self.proxy_url = get_key("IPROYAL_PROXY_URL")
    def get_proxy(self) -> Optional[dict]:
        if not self.proxy_url: return None
        return {"server": self.proxy_url}


class StealthBrowser:
    """Stealth browser with advanced anti-detection"""

    def __init__(self,
                 user_data_dir: str = None,
                 headless: bool = False,
                 use_proxy: bool = False):
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.proxy_manager = ProxyManager() if use_proxy else None
        self.playwright = None
        self.browser = None
        self.context = None
        self.stealth_engine = Stealth()

    def _get_stealth_args(self):
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--disable-extensions",
            "--lang=en-US,en",
        ]

    def launch(self) -> 'StealthBrowser':
        self.playwright = sync_playwright().start()
        ua = random.choice(USER_AGENTS)
        res = random.choice(RESOLUTIONS)
        proxy = self.proxy_manager.get_proxy() if self.proxy_manager else None

        launch_options = {
            "headless": self.headless,
            "args": self._get_stealth_args(),
        }

        context_options = {
            "user_agent": ua,
            "viewport": res,
            "locale": "en-US",
            "timezone_id": "America/Denver",
            "ignore_https_errors": True,
        }

        if proxy:
            context_options["proxy"] = proxy

        if self.user_data_dir:
            os.makedirs(self.user_data_dir, exist_ok=True)
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                **{**launch_options, **context_options}
            )
        else:
            self.browser = self.playwright.chromium.launch(**launch_options)
            self.context = self.browser.new_context(**context_options)

        # Apply stealth to initial page if any
        if self.context.pages:
            self.stealth_engine.apply_stealth_sync(self.context.pages[0])

        print(f"[Browser] Launched (UA: {ua[:40]}... Proxy: {bool(proxy)})")
        return self

    def new_page(self) -> Page:
        page = self.context.new_page()
        self.stealth_engine.apply_stealth_sync(page)
        return page

    def close(self):
        if self.context: self.context.close()
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()
        print("[Browser] Closed")

    def __enter__(self): return self.launch()
    def __exit__(self, *args): self.close()


class HumanTyping:
    @staticmethod
    def type(page: Page, selector: str, text: str, delay_range: tuple = (40, 120)):
        element = page.locator(selector)
        element.click()
        for char in text:
            element.type(char, delay=random.randint(*delay_range))
            if random.random() < 0.08:
                time.sleep(random.uniform(0.1, 0.4))

    @staticmethod
    def click(page: Page, selector: str):
        element = page.locator(selector)
        element.hover()
        time.sleep(random.uniform(0.1, 0.3))
        element.click()


def create_stealth_browser(session_name: str = None,
                           headless: bool = False,
                           use_proxy: bool = False) -> StealthBrowser:
    user_data_dir = None
    if session_name:
        user_data_dir = f"E:/0x/browser_sessions/{session_name}/profile"
    return StealthBrowser(user_data_dir=user_data_dir, headless=headless, use_proxy=use_proxy)

if __name__ == "__main__":
    print("Testing stealth browser v2.1...")
    with create_stealth_browser("test_v2_1") as browser:
        page = browser.new_page()
        page.goto("https://bot.sannysoft.com/")
        time.sleep(5)
        page.screenshot(path="E:/0x/stealth_test_v2_1.png")
        print("Verification: E:/0x/stealth_test_v2_1.png")
