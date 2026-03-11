import os

# --- HARDWARE ISOLATION (APOLLO MODE) ---
# GPU 0: System/Noise
# GPU 1: COGNITION & PERCEPTION (Ollama + Whisper + Kokoro)
# GPU 2: RESERVED (Dedicated 12GB Memory System)
AGENCY_GPU_INDEX = "1" 

# --- SENSORY CONFIG ---
SAMPLING_RATE = 16000
VAD_THRESHOLD = 0.4 
WHISPER_MODEL = "base" 
WHISPER_COMPUTE_TYPE = "int8"
TURN_CONCLUSION_DELAY = 2.0 # Wait 2 seconds of silence before concluding user turn

# --- TTS CONFIG ---
KOKORO_MODEL_PATH = "kokoro-v1.0.onnx"
KOKORO_VOICES_PATH = "voices-v1.0.bin"
DEFAULT_VOICE = "am_adam" 

# --- COGNITIVE LINK ---
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3n:e4b"

# --- LOGGING ---
LOG_DIR = r"E:\0x\logs\agency"
os.makedirs(LOG_DIR, exist_ok=True)
