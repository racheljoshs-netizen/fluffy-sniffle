import os
import sys
from pathlib import Path

# Add parent directory to path to reach agency package
sys.path.append(str(Path(__file__).parent.parent))

import espeakng_loader
from kokoro_onnx import Kokoro
import logging
from agency import config

logging.basicConfig(level=logging.INFO)

def test_init():
    print("Checking espeakng-loader...")
    try:
        lib_path = espeakng_loader.get_library_path()
        data_path = espeakng_loader.get_data_path()
        print(f"Library: {lib_path}")
        print(f"Data: {data_path}")
    except Exception as e:
        print(f"espeakng-loader failed: {e}")
        return

    print("\nAttempting Kokoro Initialization...")
    model_path = os.path.join("agency", config.KOKORO_MODEL_PATH)
    voice_path = os.path.join("agency", config.KOKORO_VOICES_PATH)
    
    print(f"Loading Model: {model_path}")
    print(f"Loading Voices: {voice_path}")

    if not os.path.exists(model_path):
        print(f"Error: {model_path} missing.")
        return

    try:
        kokoro = Kokoro(model_path, voice_path)
        print("SUCCESS: Kokoro initialized successfully.")
        
        # Test phonemization
        print("Testing phonemization...")
        samples, sample_rate = kokoro.create("Hello mothership.", voice="af_heart", speed=1.0, lang="en-us")
        print(f"SUCCESS: Generated {len(samples)} samples at {sample_rate}Hz.")
        
    except Exception as e:
        print(f"Kokoro initialization/test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_init()
