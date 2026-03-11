import requests
import time
from phoenix.config import CAPMONSTER_API_KEY

class CaptchaSolver:
    BASE_URL = "https://api.capmonster.cloud"
    
    @staticmethod
    def solve_turnstile(website_url, website_key):
        return CaptchaSolver._create_and_wait_task({
            "type": "TurnstileTaskProxyless",
            "websiteURL": website_url,
            "websiteKey": website_key
        })

    @staticmethod
    def _create_and_wait_task(task_payload):
        try:
            create_payload = {"clientKey": CAPMONSTER_API_KEY, "task": task_payload}
            resp = requests.post(f"{CaptchaSolver.BASE_URL}/createTask", json=create_payload)

            if resp.status_code != 200: return None
            
            task_id = resp.json().get("taskId")
            if not task_id: return None
            
            start_time = time.time()
            while time.time() - start_time < 120:
                time.sleep(2)
                res_resp = requests.post(f"{CaptchaSolver.BASE_URL}/getTaskResult", json={"clientKey": CAPMONSTER_KEY, "taskId": task_id})
                data = res_resp.json()
                if data.get("status") == "ready":
                    return data.get("solution", {}).get("token") or data.get("solution", {}).get("gRecaptchaResponse")
                elif data.get("status") == "processing": continue
                else: return None
            return None
        except Exception: return None
