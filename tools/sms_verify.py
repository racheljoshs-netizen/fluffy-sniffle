"""
SMS Verification Service v2.0
Supports: SMS-Activate, 5sim, and others
"""

import requests
import time
import os
from typing import Optional, Tuple

# Local imports
try:
    from config_loader import get_key
except ImportError:
    def get_key(name, default=None): return os.getenv(name, default)

SMS_ACTIVATE_KEY = get_key("SMS_ACTIVATE_KEY")
FIVESIM_KEY = get_key("FIVESIM_KEY")

# Service codes for SMS-Activate
SERVICE_CODES = {
    "tiktok": "ds",
    "instagram": "ig",
    "twitter": "tw",
    "facebook": "fb",
    "google": "go",
    "discord": "ds",
    "telegram": "tg",
    "whatsapp": "wa",
}

# Country codes
COUNTRY_CODES = {
    "us": 187,
    "uk": 16,
    "russia": 0,
    "india": 22,
    "indonesia": 6,
}


class SMSActivate:
    """SMS-Activate.org API wrapper"""

    BASE_URL = "https://api.sms-activate.org/stubs/handler_api.php"

    def __init__(self, api_key: str = SMS_ACTIVATE_KEY):
        self.api_key = api_key
        if not api_key:
            print("[SMS] WARNING: No SMS-Activate API key set!")

    def _request(self, action: str, **params) -> str:
        params["api_key"] = self.api_key
        params["action"] = action
        resp = requests.get(self.BASE_URL, params=params, timeout=30)
        return resp.text

    def get_balance(self) -> float:
        result = self._request("getBalance")
        if result.startswith("ACCESS_BALANCE:"):
            return float(result.split(":")[1])
        return 0.0

    def get_number(self, service: str, country: str = "us") -> Optional[Tuple[str, str]]:
        if not self.api_key:
            return None

        service_code = SERVICE_CODES.get(service.lower(), service)
        country_code = COUNTRY_CODES.get(country.lower(), country)

        result = self._request(
            "getNumber",
            service=service_code,
            country=country_code
        )

        if result.startswith("ACCESS_NUMBER:"):
            parts = result.split(":")
            activation_id = parts[1]
            phone = parts[2]
            print(f"[SMS] Got number: {phone} (ID: {activation_id})")
            return (phone, activation_id)
        else:
            print(f"[SMS] Error getting number: {result}")
            return None

    def get_code(self, activation_id: str, timeout: int = 120) -> Optional[str]:
        print(f"[SMS] Waiting for code (timeout: {timeout}s)...")
        start = time.time()

        while time.time() - start < timeout:
            result = self._request("getStatus", id=activation_id)
            if result.startswith("STATUS_OK:"):
                code = result.split(":")[1]
                print(f"[SMS] Got code: {code}")
                return code
            elif result == "STATUS_WAIT_CODE":
                time.sleep(3)
            elif result == "STATUS_CANCEL":
                return None
            time.sleep(3)
        return None

    def set_status(self, activation_id: str, status: int) -> bool:
        result = self._request("setStatus", id=activation_id, status=status)
        return result.startswith("ACCESS")

    def cancel(self, activation_id: str) -> bool:
        return self.set_status(activation_id, 8)

    def complete(self, activation_id: str) -> bool:
        return self.set_status(activation_id, 6)

# Unified Interface
class SMSVerification:
    def __init__(self, provider: str = "sms-activate"):
        if provider == "sms-activate":
            self.service = SMSActivate()
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_number(self, service: str, country: str = "us") -> Optional[Tuple[str, str]]:
        return self.service.get_number(service, country)

    def get_code(self, activation_id: str, timeout: int = 120) -> Optional[str]:
        return self.service.get_code(activation_id, timeout)

    def complete(self, activation_id: str) -> bool:
        return self.service.complete(activation_id)

    def cancel(self, activation_id: str) -> bool:
        return self.service.cancel(activation_id)

if __name__ == "__main__":
    sms = SMSActivate()
    if sms.api_key:
        print(f"SMS-Activate Balance: ${sms.get_balance():.2f}")
    else:
        print("No SMS_ACTIVATE_KEY in environment or config.")
