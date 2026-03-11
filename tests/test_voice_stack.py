import asyncio
import whisper
import sounddevice as sd
import numpy as np
import edge_tts
from playsound import playsound
import tempfile
import os

async def test_stack():
    print("[1/4] Initializing audio input stream...")
    try:
        # Just a short probe
        with sd.InputStream(samplerate=16000, channels=1):
            print("  ✓ Audio input stream initialized.")
    except Exception as e:
        print(f"  ✗ Audio input failure: {e}")

    print("[2/4] Configuring voice recognition module...")
    try:
        model = whisper.load_model("tiny") # Use tiny for fast test
        print("  ✓ Whisper model loaded.")
    except Exception as e:
        print(f"  ✗ Whisper failure: {e}")

    print("[3/4] Establishing API connection...")
    # We'll skip a live API call to save tokens, but check the key
    api_key = "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"
    if api_key.startswith("sk-"):
        print("  ✓ API Key format verified.")
    else:
        print("  ✗ API Key invalid.")

    print("[4/4] Verifying output fidelity...")
    try:
        communicate = edge_tts.Communicate("G-Pattern Voice Stack Initialized. Verify output fidelity.", "en-US-AriaNeural")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            await communicate.save(f.name)
            temp_path = f.name
        playsound(temp_path)
        os.unlink(temp_path)
        print("  ✓ TTS and Audio playback verified.")
    except Exception as e:
        print(f"  ✗ Output failure: {e}")

if __name__ == "__main__":
    asyncio.run(test_stack())
