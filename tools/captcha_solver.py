"""
Universal CAPTCHA Solver
Uses CapMonster Cloud API
Supports: reCAPTCHA, hCaptcha, Turnstile, FunCaptcha, GeeTest
"""

import requests
import time
import re
from typing import Optional, Dict, Any

CAPMONSTER_KEY = "5c0a9d4fd3e561d41d34ae13d8abc4c8"
BASE_URL = "https://api.capmonster.cloud"


class CaptchaSolver:
    """Universal CAPTCHA solver using CapMonster Cloud"""
    
    def __init__(self, api_key: str = CAPMONSTER_KEY):
        self.api_key = api_key
        self.timeout = 120  # seconds
    
    def _create_task(self, task: Dict[str, Any]) -> Optional[int]:
        """Create a task and return task ID"""
        try:
            resp = requests.post(
                f"{BASE_URL}/createTask",
                json={"clientKey": self.api_key, "task": task},
                timeout=30
            )
            data = resp.json()
            if data.get("errorId") == 0:
                return data.get("taskId")
            print(f"[Captcha] Error creating task: {data.get('errorDescription')}")
            return None
        except Exception as e:
            print(f"[Captcha] Request error: {e}")
            return None
    
    def _get_result(self, task_id: int) -> Optional[str]:
        """Poll for task result"""
        start = time.time()
        while time.time() - start < self.timeout:
            try:
                resp = requests.post(
                    f"{BASE_URL}/getTaskResult",
                    json={"clientKey": self.api_key, "taskId": task_id},
                    timeout=30
                )
                data = resp.json()
                
                if data.get("status") == "ready":
                    solution = data.get("solution", {})
                    # Different CAPTCHA types return different keys
                    return (
                        solution.get("token") or
                        solution.get("gRecaptchaResponse") or
                        solution.get("text") or
                        solution.get("challenge")
                    )
                elif data.get("status") == "processing":
                    time.sleep(2)
                else:
                    print(f"[Captcha] Error: {data.get('errorDescription')}")
                    return None
            except Exception as e:
                print(f"[Captcha] Poll error: {e}")
                time.sleep(2)
        
        print("[Captcha] Timeout waiting for solution")
        return None
    
    def solve(self, task: Dict[str, Any]) -> Optional[str]:
        """Create task and wait for solution"""
        task_id = self._create_task(task)
        if not task_id:
            return None
        print(f"[Captcha] Task created: {task_id}")
        return self._get_result(task_id)
    
    # ===== Specific CAPTCHA Types =====
    
    def solve_recaptcha_v2(self, website_url: str, website_key: str, 
                           invisible: bool = False) -> Optional[str]:
        """Solve reCAPTCHA v2"""
        print(f"[Captcha] Solving reCAPTCHA v2 for {website_url}")
        return self.solve({
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": website_url,
            "websiteKey": website_key,
            "isInvisible": invisible
        })
    
    def solve_recaptcha_v3(self, website_url: str, website_key: str,
                           action: str = "verify", min_score: float = 0.3) -> Optional[str]:
        """Solve reCAPTCHA v3"""
        print(f"[Captcha] Solving reCAPTCHA v3 for {website_url}")
        return self.solve({
            "type": "RecaptchaV3TaskProxyless",
            "websiteURL": website_url,
            "websiteKey": website_key,
            "pageAction": action,
            "minScore": min_score
        })
    
    def solve_hcaptcha(self, website_url: str, website_key: str) -> Optional[str]:
        """Solve hCaptcha"""
        print(f"[Captcha] Solving hCaptcha for {website_url}")
        return self.solve({
            "type": "HCaptchaTaskProxyless",
            "websiteURL": website_url,
            "websiteKey": website_key
        })
    
    def solve_turnstile(self, website_url: str, website_key: str) -> Optional[str]:
        """Solve Cloudflare Turnstile"""
        print(f"[Captcha] Solving Turnstile for {website_url}")
        return self.solve({
            "type": "TurnstileTaskProxyless",
            "websiteURL": website_url,
            "websiteKey": website_key
        })
    
    def solve_funcaptcha(self, website_url: str, website_key: str,
                         subdomain: str = None) -> Optional[str]:
        """Solve FunCaptcha/Arkose Labs"""
        print(f"[Captcha] Solving FunCaptcha for {website_url}")
        task = {
            "type": "FunCaptchaTaskProxyless",
            "websiteURL": website_url,
            "websitePublicKey": website_key
        }
        if subdomain:
            task["funcaptchaApiJSSubdomain"] = subdomain
        return self.solve(task)
    
    def solve_geetest(self, website_url: str, gt: str, challenge: str,
                      api_server: str = None) -> Optional[Dict]:
        """Solve GeeTest"""
        print(f"[Captcha] Solving GeeTest for {website_url}")
        task = {
            "type": "GeeTestTaskProxyless",
            "websiteURL": website_url,
            "gt": gt,
            "challenge": challenge
        }
        if api_server:
            task["geetestApiServerSubdomain"] = api_server
        return self.solve(task)
    
    def solve_image(self, image_base64: str) -> Optional[str]:
        """Solve image-based CAPTCHA (text recognition)"""
        print("[Captcha] Solving image CAPTCHA")
        return self.solve({
            "type": "ImageToTextTask",
            "body": image_base64
        })
    
    # ===== Auto-Detection =====
    
    def detect_and_solve(self, page) -> Optional[str]:
        """
        Auto-detect CAPTCHA type on page and solve it.
        Works with Playwright page object.
        """
        html = page.content()
        url = page.url
        
        # Check for reCAPTCHA
        recaptcha_match = re.search(r'data-sitekey="([^"]+)"', html)
        if recaptcha_match or "recaptcha" in html.lower():
            site_key = recaptcha_match.group(1) if recaptcha_match else None
            if not site_key:
                # Try to find in script
                site_key = re.search(r"sitekey['\"]?\s*[:=]\s*['\"]([^'\"]+)", html)
                site_key = site_key.group(1) if site_key else None
            
            if site_key:
                if "recaptcha/api.js?render=" in html:
                    return self.solve_recaptcha_v3(url, site_key)
                else:
                    return self.solve_recaptcha_v2(url, site_key)
        
        # Check for hCaptcha
        hcaptcha_match = re.search(r'data-sitekey="([^"]+)".*?hcaptcha', html, re.DOTALL)
        if hcaptcha_match or "hcaptcha" in html.lower():
            site_key = hcaptcha_match.group(1) if hcaptcha_match else None
            if not site_key:
                site_key = re.search(r'sitekey["\']?\s*[:=]\s*["\']([^"\']+)', html)
                site_key = site_key.group(1) if site_key else None
            if site_key:
                return self.solve_hcaptcha(url, site_key)
        
        # Check for Turnstile
        if "turnstile" in html.lower() or "challenges.cloudflare.com" in html:
            site_key = re.search(r'data-sitekey="([^"]+)"', html)
            if site_key:
                return self.solve_turnstile(url, site_key.group(1))
        
        # Check for FunCaptcha
        if "funcaptcha" in html.lower() or "arkoselabs" in html.lower():
            pub_key = re.search(r'publicKey["\']?\s*[:=]\s*["\']([^"\']+)', html)
            if pub_key:
                return self.solve_funcaptcha(url, pub_key.group(1))
        
        print("[Captcha] No CAPTCHA detected or unsupported type")
        return None


# Convenience instance
solver = CaptchaSolver()


if __name__ == "__main__":
    # Test balance check
    resp = requests.post(
        f"{BASE_URL}/getBalance",
        json={"clientKey": CAPMONSTER_KEY}
    )
    print(f"CapMonster Balance: ${resp.json().get('balance', 0):.2f}")
