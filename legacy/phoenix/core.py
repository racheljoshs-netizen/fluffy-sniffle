from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import os
import logging
from phoenix import config
from phoenix.stealth import StealthOps

class PhoenixController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.active = False

    def launch(self, profile_id="default", use_proxy=False):
        logging.info(f"[Phoenix] Launching Identity: {profile_id}...")
        
        # Proxy Selection
        proxy_config = None
        if use_proxy and config.PROXIES:
            import random
            selected = random.choice(config.PROXIES)
            logging.info(f"[Phoenix] Proxy Active: {selected}")
            proxy_config = {"server": selected}

        profile_path = config.get_task_profile(profile_id)
        
        self.playwright = sync_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--start-maximized"
        ]

        try:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=config.HEADLESS,
                devtools=config.DEVTOOLS,
                viewport=config.VIEWPORT,
                user_agent=config.CHROME_UA,
                proxy=proxy_config,
                args=args,
                downloads_path=config.DOWNLOADS_DIR,
                accept_downloads=True
            )
            
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            
            # INJECT STEALTH
            stealth_sync(self.page)
            
            # Additional WebRTC Leak Prevention
            self.page.add_init_script("""
                const defaultGetUserMedia = navigator.mediaDevices.getUserMedia;
                const defaultEnumerateDevices = navigator.mediaDevices.enumerateDevices;
                navigator.mediaDevices.getUserMedia = (constraints) => Promise.resolve(null);
                navigator.mediaDevices.enumerateDevices = () => Promise.resolve([]);
            """)
            
            self.active = True
            return self

        except Exception as e:
            logging.error(f"[Phoenix] Launch Failed: {e}")
            self.close()
            return None

    def goto(self, url):
        if not self.active: return False
        try:
            logging.info(f"[Phoenix] Navigating: {url}")
            self.page.goto(url, wait_until="domcontentloaded")
            return True
        except Exception as e: 
            logging.error(f"[Phoenix] Nav Error: {e}")
            return False

    def close(self):
        if self.active:
            logging.info("[Phoenix] Shutting down...")
            try:
                if self.context: self.context.close()
                if self.playwright: self.playwright.stop()
            except Exception as e:
                logging.error(f"[Phoenix] Shutdown Error: {e}")
            self.active = False

    # Wrappers for StealthOps
    def type(self, selector, text):
        if self.active: StealthOps.human_type(self.page, selector, text)

    def click(self, selector):
        if self.active: StealthOps.human_click(self.page, selector)

    def wait_for_stable(self, seconds=2):
        time.sleep(seconds)
        try: self.page.mouse.wheel(0, 100)
        except: pass

    def smart_click(self, target_desc, selectors=None):
        if not self.active: return False
        # Try specific selectors first
        if selectors:
            for s in selectors:
                try: 
                    if self.page.is_visible(s):
                        self.click(s)
                        return True
                except: pass
        # Fallback to text matching
        try:
            el = self.page.get_by_text(target_desc, exact=False).first
            if el.is_visible():
                el.scroll_into_view_if_needed()
                StealthOps.human_click(self.page, f"text={target_desc}")
                return True
        except: pass
        return False

    def smart_type(self, target_desc, text, selectors=None):
        if not self.active: return False
        if selectors:
            for s in selectors:
                try:
                    if self.page.is_visible(s):
                        self.type(s, text)
                        return True
                except: pass
        try:
            el = self.page.get_by_label(target_desc).first
            if el.is_visible():
                el.focus()
                StealthOps.human_type(self.page, ":focus", text)
                return True
        except: pass
        return False
        
    def screenshot(self, filename):
        if self.active:
            path = os.path.join(config.SCREENSHOT_DIR, f"{filename}.png")
            try: self.page.screenshot(path=path, full_page=True)
            except: pass
            logging.info(f"[Phoenix] Snap: {filename}")
