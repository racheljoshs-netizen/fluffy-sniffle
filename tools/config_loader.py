import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory (E:\0x)
BASE_DIR = Path("E:/0x")

# Load .env
load_dotenv(BASE_DIR / ".env")

# Additional keys from chariot_env.txt if it exists
chariot_env = BASE_DIR / "chariot_env.txt"
if chariot_env.exists():
    with open(chariot_env, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                if not os.getenv(key):
                    os.environ[key] = value

def get_key(name: str, default: str = None) -> str:
    """Get key from environment"""
    return os.getenv(name, default)

# Common Keys
OPENROUTER_API_KEY = get_key("OPENROUTER_API_KEY")
CAPMONSTER_API_KEY = get_key("CAPMONSTER_API_KEY")
SMS_ACTIVATE_KEY = get_key("SMS_ACTIVATE_KEY")
IPROYAL_PROXY_URL = get_key("IPROYAL_PROXY_URL")
