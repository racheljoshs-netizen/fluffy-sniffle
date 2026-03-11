import sounddevice as sd
import numpy as np
import torch
import time

# Load VAD for testing
model_vad, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    
    audio_float32 = indata.flatten()
    # Calculate energy
    energy = np.linalg.norm(audio_float32)
    
    # Calculate VAD probability
    with torch.no_grad():
        confidence = model_vad(torch.from_numpy(audio_float32), 16000).item()
    
    if confidence > 0.3:
        bar = "█" * int(confidence * 50)
        print(f"VAD: {confidence:.2f} | Energy: {energy:.4f} | {bar}")

print("--- MIC PERCEPTION TEST ---")
print("Speak into your Fifine Microphone...")
print("If you see VAD bars, the hardware is working.")

try:
    with sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=callback, blocksize=512):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("
Test Ended.")
