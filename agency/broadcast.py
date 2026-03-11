import os
import sys
from pathlib import Path
import asyncio
import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agency import config

# Force GPU 2
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

async def broadcast():
    print("Initializing Proof of Life Broadcast...")
    model_path = os.path.join("agency", config.KOKORO_MODEL_PATH)
    voice_path = os.path.join("agency", config.KOKORO_VOICES_PATH)
    
    kokoro = Kokoro(model_path, voice_path)
    text = "Architect, I am speaking through the GPU two perception cluster. The hardware link is active. The mothership is listening."
    
    print(f"Generating voice on GPU 2: {text}")
    samples, sample_rate = kokoro.create(text, voice="am_adam", speed=1.0, lang="en-us")
    
    print("Broadcasting through speakers...")
    # Play via sounddevice
    sd.play(samples, sample_rate)
    sd.wait()
    print("Broadcast complete.")

if __name__ == "__main__":
    try:
        asyncio.run(broadcast())
    except Exception as e:
        print(f"Broadcast Failed: {e}")
