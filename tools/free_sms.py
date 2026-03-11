"""
Free SMS Verification
Scrapes public free SMS receiver sites

WARNING: These numbers are public - everyone can see the codes.
They're often already blocked by major platforms.
But they're FREE.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional

class FreeSMSReceiver:
    """Scrape free SMS receiver websites"""
    
    SOURCES = [
        {
            "name": "receive-smss.com",
            "list_url": "https://receive-smss.com/",
            "sms_url": "https://receive-smss.com/sms/{number}/",
        },
        {
            "name": "freephonenum.com", 
            "list_url": "https://freephonenum.com/",
            "sms_url": "https://freephonenum.com/{number}",
        },
        {
            "name": "receivesms.cc",
            "list_url": "https://receivesms.cc/",
            "sms_url": "https://receivesms.cc/us-phone-number/{number}",
        },
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_available_numbers(self, country: str = "us") -> List[Dict]:
        """Get list of available free phone numbers"""
        numbers = []
        
        # Try receive-smss.com
        try:
            resp = self.session.get("https://receive-smss.com/", timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find number links
            for link in soup.find_all('a', href=re.compile(r'/sms/\+?\d+')):
                href = link.get('href', '')
                match = re.search(r'/sms/(\+?\d+)', href)
                if match:
                    num = match.group(1)
                    if country.lower() == "us" and num.startswith("+1"):
                        numbers.append({
                            "number": num,
                            "source": "receive-smss.com",
                            "url": f"https://receive-smss.com/sms/{num}/"
                        })
        except Exception as e:
            print(f"[FreeSMS] receive-smss.com error: {e}")
        
        # Try freephonenum.com
        try:
            resp = self.session.get("https://freephonenum.com/", timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for link in soup.find_all('a', href=re.compile(r'/\d+')):
                href = link.get('href', '')
                match = re.search(r'/(\d{10,})', href)
                if match:
                    num = match.group(1)
                    numbers.append({
                        "number": num,
                        "source": "freephonenum.com",
                        "url": f"https://freephonenum.com/{num}"
                    })
        except Exception as e:
            print(f"[FreeSMS] freephonenum.com error: {e}")
        
        print(f"[FreeSMS] Found {len(numbers)} free numbers")
        return numbers
    
    def get_recent_sms(self, number_url: str) -> List[Dict]:
        """Get recent SMS messages for a number"""
        messages = []
        
        try:
            resp = self.session.get(number_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for message containers (varies by site)
            # Try common patterns
            for msg_div in soup.find_all(['div', 'tr'], class_=re.compile(r'message|sms|row')):
                text = msg_div.get_text(strip=True)
                if text and len(text) > 5:
                    # Try to extract code
                    code_match = re.search(r'\b(\d{4,8})\b', text)
                    messages.append({
                        "text": text[:200],
                        "code": code_match.group(1) if code_match else None
                    })
        except Exception as e:
            print(f"[FreeSMS] Error getting SMS: {e}")
        
        return messages
    
    def wait_for_code(self, number_url: str, timeout: int = 120) -> Optional[str]:
        """Wait for a verification code to arrive"""
        print(f"[FreeSMS] Waiting for code at {number_url}...")
        
        # Get initial messages
        initial_msgs = self.get_recent_sms(number_url)
        initial_codes = {m.get('code') for m in initial_msgs if m.get('code')}
        
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(5)
            
            current_msgs = self.get_recent_sms(number_url)
            for msg in current_msgs:
                code = msg.get('code')
                if code and code not in initial_codes:
                    print(f"[FreeSMS] Got new code: {code}")
                    return code
            
            print(f"[FreeSMS] Still waiting... ({int(time.time() - start)}s)")
        
        print("[FreeSMS] Timeout - no new code received")
        return None


class TextNowAutomation:
    """
    TextNow - Free US phone number app
    Requires app install but gives you a PRIVATE free number
    """
    
    @staticmethod
    def instructions():
        return """
        TextNow - FREE Private US Phone Number
        
        1. Download TextNow app (Android/iOS) or use web: https://www.textnow.com
        2. Sign up with email (no phone needed)
        3. You get a FREE US phone number
        4. Use this number for ALL verifications
        5. Check TextNow app/web for incoming SMS
        
        This is the BEST free option because:
        - It's YOUR number (private)
        - Not shared/blocked like public receivers
        - Works with most services
        - Completely free
        """


class GoogleVoiceAutomation:
    """
    Google Voice - Free US phone number
    Requires existing US number to set up (one-time)
    """
    
    @staticmethod
    def instructions():
        return """
        Google Voice - FREE US Phone Number
        
        1. Go to: https://voice.google.com
        2. Sign in with Google account
        3. You need to verify with an existing US number ONCE
        4. After that, you have a free permanent US number
        5. Use this for all verifications
        
        If you already have a cell phone:
        - Use it once to set up Google Voice
        - Then use Google Voice number for everything else
        - Keeps your real number private
        """


# ===== Main =====

def find_free_numbers():
    """Find and display available free numbers"""
    sms = FreeSMSReceiver()
    numbers = sms.get_available_numbers("us")
    
    print("\n=== FREE US PHONE NUMBERS ===")
    print("WARNING: These are PUBLIC - everyone can see SMS!")
    print("Major platforms often BLOCK these numbers.\n")
    
    for n in numbers[:10]:
        print(f"  {n['number']} - {n['source']}")
        print(f"    View SMS: {n['url']}")
    
    print("\n=== BETTER FREE OPTIONS ===")
    print(TextNowAutomation.instructions())


if __name__ == "__main__":
    find_free_numbers()
