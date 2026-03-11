"""
Social Media Automation Module
Combines: Stealth Browser + CAPTCHA Solver + SMS Verification

Usage:
    from social_automation import SocialAutomation
    
    auto = SocialAutomation()
    auto.tiktok_login("email", "password")
    auto.tiktok_upload_profile_pic("path/to/image.png")
    auto.tiktok_post_video("path/to/video.mp4", "caption")
"""

import time
import os
from typing import Optional

from stealth_browser import create_stealth_browser, HumanTyping, SessionManager
from captcha_solver import CaptchaSolver
from sms_verify import SMSVerification


class SocialAutomation:
    """
    Unified social media automation
    """
    
    def __init__(self, session_prefix: str = "social"):
        self.session_prefix = session_prefix
        self.sessions = SessionManager()
        self.captcha = CaptchaSolver()
        self.sms = None  # Initialize when needed
        
        # Screenshot directory
        self.screenshot_dir = "E:/G/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _screenshot(self, page, name: str):
        """Save a screenshot"""
        path = os.path.join(self.screenshot_dir, f"{name}.png")
        page.screenshot(path=path)
        print(f"[Screenshot] Saved: {path}")
        return path
    
    def _handle_captcha(self, page) -> bool:
        """Detect and solve CAPTCHA if present"""
        try:
            token = self.captcha.detect_and_solve(page)
            if token:
                print(f"[CAPTCHA] Solved! Token: {token[:20]}...")
                # TODO: Inject token into page based on CAPTCHA type
                return True
        except Exception as e:
            print(f"[CAPTCHA] Error: {e}")
        return False
    
    # ===== TIKTOK =====
    
    def tiktok_login(self, email: str, password: str) -> bool:
        """Login to TikTok"""
        print("[TikTok] Starting login...")
        
        session_dir = f"{self.session_prefix}_tiktok"
        
        with create_stealth_browser(session_dir) as browser:
            page = browser.new_page()
            
            # Go to login page
            page.goto("https://www.tiktok.com/login/phone-or-email/email")
            time.sleep(3)
            self._screenshot(page, "tiktok_1_login_page")
            
            # Fill email
            try:
                email_input = page.locator('input[name="username"]')
                HumanTyping.type(page, 'input[name="username"]', email)
                print("[TikTok] Filled email")
            except Exception as e:
                print(f"[TikTok] Email input error: {e}")
                return False
            
            # Fill password
            try:
                HumanTyping.type(page, 'input[type="password"]', password)
                print("[TikTok] Filled password")
            except Exception as e:
                print(f"[TikTok] Password input error: {e}")
                return False
            
            self._screenshot(page, "tiktok_2_filled")
            
            # Click login
            try:
                page.locator('button[type="submit"]').click()
                print("[TikTok] Clicked login")
                time.sleep(5)
            except Exception as e:
                print(f"[TikTok] Login button error: {e}")
            
            self._screenshot(page, "tiktok_3_after_login")
            
            # Check for CAPTCHA
            html = page.content()
            if "captcha" in html.lower() or "verify" in html.lower():
                print("[TikTok] CAPTCHA detected, attempting to solve...")
                self._handle_captcha(page)
                time.sleep(3)
                self._screenshot(page, "tiktok_4_after_captcha")
            
            # Check if logged in
            page.goto("https://www.tiktok.com/@wristcream_hq")
            time.sleep(3)
            self._screenshot(page, "tiktok_5_profile")
            
            # Look for edit profile button (indicates logged in)
            if page.locator('[data-e2e="edit-profile"]').count() > 0:
                print("[TikTok] Login successful!")
                return True
            else:
                print("[TikTok] Login may have failed")
                return False
    
    def tiktok_upload_profile_pic(self, image_path: str) -> bool:
        """Upload profile picture to TikTok"""
        print("[TikTok] Uploading profile picture...")
        
        session_dir = f"{self.session_prefix}_tiktok"
        
        with create_stealth_browser(session_dir) as browser:
            page = browser.new_page()
            
            # Go to profile
            page.goto("https://www.tiktok.com/@wristcream_hq")
            time.sleep(3)
            
            # Click edit profile
            edit_btn = page.locator('[data-e2e="edit-profile"]')
            if edit_btn.count() > 0:
                edit_btn.click()
                time.sleep(2)
                self._screenshot(page, "tiktok_edit_profile")
                
                # Look for photo upload
                file_input = page.locator('input[type="file"][accept*="image"]')
                if file_input.count() > 0:
                    file_input.set_input_files(image_path)
                    time.sleep(3)
                    self._screenshot(page, "tiktok_photo_uploaded")
                    
                    # Save changes
                    save_btn = page.locator('button:has-text("Save")')
                    if save_btn.count() > 0:
                        save_btn.click()
                        time.sleep(2)
                        print("[TikTok] Profile picture uploaded!")
                        return True
            
            print("[TikTok] Could not upload profile picture")
            return False
    
    def tiktok_post_video(self, video_path: str, caption: str) -> bool:
        """Post a video to TikTok"""
        print("[TikTok] Posting video...")
        
        session_dir = f"{self.session_prefix}_tiktok"
        
        with create_stealth_browser(session_dir) as browser:
            page = browser.new_page()
            
            # Go to upload page
            page.goto("https://www.tiktok.com/upload")
            time.sleep(3)
            self._screenshot(page, "tiktok_upload_page")
            
            # Upload video
            file_input = page.locator('input[type="file"][accept*="video"]')
            if file_input.count() > 0:
                file_input.set_input_files(video_path)
                time.sleep(5)  # Wait for upload
                self._screenshot(page, "tiktok_video_uploaded")
                
                # Add caption
                caption_input = page.locator('[data-e2e="upload-caption"]')
                if caption_input.count() > 0:
                    caption_input.fill(caption)
                
                # Post
                post_btn = page.locator('button:has-text("Post")')
                if post_btn.count() > 0:
                    post_btn.click()
                    time.sleep(5)
                    print("[TikTok] Video posted!")
                    return True
            
            print("[TikTok] Could not post video")
            return False
    
    # ===== PINTEREST =====
    
    def pinterest_login(self, email: str, password: str) -> bool:
        """Login to Pinterest"""
        print("[Pinterest] Starting login...")
        
        session_dir = f"{self.session_prefix}_pinterest"
        
        with create_stealth_browser(session_dir) as browser:
            page = browser.new_page()
            
            page.goto("https://www.pinterest.com/login/")
            time.sleep(3)
            self._screenshot(page, "pinterest_1_login")
            
            # Fill email
            HumanTyping.type(page, '#email', email)
            print("[Pinterest] Filled email")
            
            # Fill password
            HumanTyping.type(page, '#password', password)
            print("[Pinterest] Filled password")
            
            self._screenshot(page, "pinterest_2_filled")
            
            # Click login
            page.locator('button[type="submit"]').click()
            time.sleep(5)
            
            self._screenshot(page, "pinterest_3_after_login")
            
            # Check if logged in
            if "feed" in page.url or page.locator('[data-test-id="header-profile"]').count() > 0:
                print("[Pinterest] Login successful!")
                return True
            
            print("[Pinterest] Login may have failed")
            return False
    
    def pinterest_create_pin(self, image_path: str, title: str, 
                             description: str, link: str, board: str = "Wrist Care") -> bool:
        """Create a pin on Pinterest"""
        print("[Pinterest] Creating pin...")
        
        session_dir = f"{self.session_prefix}_pinterest"
        
        with create_stealth_browser(session_dir) as browser:
            page = browser.new_page()
            
            page.goto("https://www.pinterest.com/pin-creation-tool/")
            time.sleep(3)
            self._screenshot(page, "pinterest_create_1")
            
            # Upload image
            file_input = page.locator('input[type="file"]')
            if file_input.count() > 0:
                file_input.set_input_files(image_path)
                time.sleep(3)
                
                # Fill title
                title_input = page.locator('[data-test-id="pin-draft-title"]')
                if title_input.count() > 0:
                    title_input.fill(title)
                
                # Fill description
                desc_input = page.locator('[data-test-id="pin-draft-description"]')
                if desc_input.count() > 0:
                    desc_input.fill(description)
                
                # Fill link
                link_input = page.locator('[data-test-id="pin-draft-link"]')
                if link_input.count() > 0:
                    link_input.fill(link)
                
                self._screenshot(page, "pinterest_create_2_filled")
                
                # Publish
                publish_btn = page.locator('button:has-text("Publish")')
                if publish_btn.count() > 0:
                    publish_btn.click()
                    time.sleep(3)
                    print("[Pinterest] Pin created!")
                    return True
            
            print("[Pinterest] Could not create pin")
            return False


# ===== CLI Interface =====

if __name__ == "__main__":
    import sys
    
    auto = SocialAutomation()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python social_automation.py tiktok-login EMAIL PASSWORD")
        print("  python social_automation.py tiktok-profile-pic IMAGE_PATH")
        print("  python social_automation.py tiktok-post VIDEO_PATH CAPTION")
        print("  python social_automation.py pinterest-login EMAIL PASSWORD")
        print("  python social_automation.py pinterest-pin IMAGE TITLE DESC LINK")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "tiktok-login":
        auto.tiktok_login(sys.argv[2], sys.argv[3])
    elif cmd == "tiktok-profile-pic":
        auto.tiktok_upload_profile_pic(sys.argv[2])
    elif cmd == "tiktok-post":
        auto.tiktok_post_video(sys.argv[2], sys.argv[3])
    elif cmd == "pinterest-login":
        auto.pinterest_login(sys.argv[2], sys.argv[3])
    elif cmd == "pinterest-pin":
        auto.pinterest_create_pin(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print(f"Unknown command: {cmd}")
