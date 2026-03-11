import os

# --- AUTHENTICATION ---
# Primary LLM Keys
OPENROUTER_API_KEY = "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"
OPENAI_API_KEY = "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"
GROK_API_KEY = "xai-dJdhqyiSUWo9rloVlBUaNJeT7gyEsa1OBihbvUd3f6BcW8Q4WoWZYhxVKxkUU9XX9jnO51xf5xf98jTY"
GOOGLE_API_KEY = "AIzaSyBVA3_uTDuda4UW-iLOC3t58ww0NrPrADE"

# Service Keys
TELEGRAM_BOT_TOKEN = "8556208663:AAGpA3hK6qEAnC9u6gdRORBy7DYo3wCaPFc"
CAPMONSTER_API_KEY = "5c0a9d4fd3e561d41d34ae13d8abc4c8"
SMSPOOL_API_KEY = "" # To be filled by user
ELEVENLABS_API_KEY = "sk_2aa1ffe5adcd7f92ce206de1dbdcaf9d59255e799f356eff"

# --- SYSTEM ---
HEADLESS_MODE = False  # Set to True for production
USER_DATA_DIR = r"E:\0x\.chrome_profile"
SCREENSHOT_DIR = r"E:\0x\logs\screenshots"
DOWNLOADS_DIR = r"E:\0x\logs\downloads"

# Compatibility Aliases for Phoenix Core
HEADLESS = HEADLESS_MODE
DEVTOOLS = False
VIEWPORT = {"width": 1280, "height": 720}
CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
TYPE_DELAY_MIN = 0.05
TYPE_DELAY_MAX = 0.2
CLICK_DELAY_MIN = 0.1
CLICK_DELAY_MAX = 0.5

# Proxy Configuration
PROXIES = []  # Load from file if needed

# Dynamic Paths
def get_task_profile(profile_id):
    return os.path.join(USER_DATA_DIR, profile_id)

# Ensure directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
