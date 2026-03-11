import os
import sys
from pathlib import Path
import torch
import numpy as np
import sounddevice as sd
import logging
import json
import requests
import queue
from faster_whisper import WhisperModel
from kokoro_onnx import Kokoro

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# CUDA DLL DISCOVERY
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin"
if os.path.exists(cuda_path):
    try:
        os.add_dll_directory(cuda_path)
        os.environ["PATH"] += os.pathsep + cuda_path
    except Exception: pass

from agency import config

# Force GPU 1
os.environ["CUDA_VISIBLE_DEVICES"] = config.AGENCY_GPU_INDEX

logging.basicConfig(level=logging.INFO)

def run_diagnostics():
    print("--- SOVEREIGN AGENCY DIAGNOSTICS ---")
    
    # 1. GPU Check
    print(f"\n[1/5] GPU Check (Target: {config.AGENCY_GPU_INDEX})")
    if torch.cuda.is_available():
        print(f"  ✓ CUDA Available. Current Device: {torch.cuda.current_device()}")
        print(f"  ✓ Device Name: {torch.cuda.get_device_name(0)}")
    else:
        print("  ✗ CUDA Not Available.")

    # 2. STT Check
    print("\n[2/5] STT Model Check (Whisper GPU 1)")
    try:
        # Use a smaller model for faster diag
        WhisperModel("tiny", device="cuda", device_index=0, compute_type="float16")
        print("  ✓ Whisper Model (tiny) loaded on GPU.")
    except Exception as e:
        print(f"  ✗ Whisper Error: {e}")

    # 3. TTS Check
    print("\n[3/5] TTS Model Check (Kokoro GPU 1)")
    try:
        import espeakng_loader
        model_path = os.path.join("agency", config.KOKORO_MODEL_PATH)
        voice_path = os.path.join("agency", config.KOKORO_VOICES_PATH)
        Kokoro(model_path, voice_path)
        print("  ✓ Kokoro initialized successfully.")
    except Exception as e:
        print(f"  ✗ Kokoro Error: {e}")

    # 4. Audio Check
    print("\n[4/5] Audio Device Check")
    try:
        devices = sd.query_devices()
        print(f"  ✓ Found {len(devices)} audio devices.")
        default_input = sd.query_devices(kind='input')
        print(f"  ✓ Default Input: {default_input['name']}")
    except Exception as e:
        print(f"  ✗ Audio Error: {e}")

    # 5. Cognitive Link Check (Ollama)
    print("\n[5/5] Ollama Link Check (GPU 1)")
    try:
        resp = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            if config.OLLAMA_MODEL in models:
                print(f"  ✓ Ollama reachable. Model '{config.OLLAMA_MODEL}' found.")
            else:
                print(f"  ! Ollama reachable, but model '{config.OLLAMA_MODEL}' NOT found.")
                print(f"    Available: {models}")
        else:
            print(f"  ✗ Ollama returned status {resp.status_code}")
    except Exception as e:
        print(f"  ✗ Ollama Unreachable: {e}")

    print("\n--- DIAGNOSTICS COMPLETE ---")

if __name__ == "__main__":
    run_diagnostics()
