"""
VoxClip v1.0 - Clipboard Audio Interface
Monitors clipboard and reads text via Kokoro TTS.
Controls:
- Ctrl+Shift+Space: Pause/Resume
- Ctrl+Shift+X: Stop & Clear Queue
"""

import os
import sys
import time
import threading
import queue
import pyperclip
import keyboard
import sounddevice as sd
import numpy as np
from pathlib import Path
from kokoro_onnx import Kokoro

# Paths
ROOT_DIR = Path("E:/0x")
AGENCY_DIR = ROOT_DIR / "agency"
sys.path.append(str(ROOT_DIR))

try:
    from agency import config
except ImportError:
    # Fallback config if not found
    class config:
        KOKORO_MODEL_PATH = "kokoro-v1.0.onnx"
        KOKORO_VOICES_PATH = "voices-v1.0.bin"
        DEFAULT_VOICE = "am_adam"
        AGENCY_GPU_INDEX = "1"

# CUDA Setup
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin"
if os.path.exists(cuda_path):
    os.environ["PATH"] += os.pathsep + cuda_path

os.environ["CUDA_VISIBLE_DEVICES"] = config.AGENCY_GPU_INDEX

class VoxClip:
    def __init__(self):
        print("[VoxClip] Initializing Engine...")
        model_path = AGENCY_DIR / config.KOKORO_MODEL_PATH
        voice_path = AGENCY_DIR / config.KOKORO_VOICES_PATH
        
        if not model_path.exists():
            print(f"[Error] Model not found at {model_path}")
            sys.exit(1)
            
        self.kokoro = Kokoro(str(model_path), str(voice_path))
        self.text_queue = queue.Queue()
        self.is_paused = False
        self.is_running = True
        self.current_stream = None
        
        # Shortcuts
        keyboard.add_hotkey('ctrl+shift+space', self.toggle_pause)
        keyboard.add_hotkey('ctrl+shift+x', self.stop_speech)
        
        print("[VoxClip] Online. Monitoring Clipboard.")
        print("Shortcuts: Ctrl+Shift+Space (Pause/Resume), Ctrl+Shift+X (Stop)")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        state = "PAUSED" if self.is_paused else "RESUMED"
        print(f"[VoxClip] {state}")
        if self.is_paused:
            sd.stop()

    def stop_speech(self):
        print("[VoxClip] STOPPING.")
        while not self.text_queue.empty():
            try:
                self.text_queue.get_nowait()
            except queue.Empty:
                break
        sd.stop()

    def speak_worker(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            try:
                text = self.text_queue.get(timeout=0.5)
                if not text.strip():
                    continue
                
                print(f"[VoxClip] Reading: {text[:50]}...")
                
                # Split long text into sentences for better responsiveness
                sentences = text.replace("\n", ". ").split(". ")
                for sentence in sentences:
                    if not self.is_running or self.is_paused:
                        break
                    
                    if not sentence.strip():
                        continue
                        
                    samples, sample_rate = self.kokoro.create(
                        sentence, 
                        voice=config.DEFAULT_VOICE, 
                        speed=1.1, 
                        lang="en-us"
                    )
                    
                    sd.play(samples, sample_rate)
                    # Wait for playback or pause/stop
                    duration = len(samples) / sample_rate
                    start_time = time.time()
                    while time.time() - start_time < duration:
                        if self.is_paused or not self.is_running:
                            sd.stop()
                            break
                        time.sleep(0.05)
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoxClip] Speech Error: {e}")

    def monitor_clipboard(self):
        last_clip = pyperclip.paste()
        while self.is_running:
            try:
                current_clip = pyperclip.paste()
                if current_clip != last_clip:
                    if current_clip.strip():
                        print("[VoxClip] New text detected.")
                        self.text_queue.put(current_clip)
                    last_clip = current_clip
                time.sleep(0.5)
            except Exception as e:
                print(f"[VoxClip] Clipboard Error: {e}")
                time.sleep(1)

    def run(self):
        t = threading.Thread(target=self.speak_worker, daemon=True)
        t.start()
        try:
            self.monitor_clipboard()
        except KeyboardInterrupt:
            self.is_running = False
            print("[VoxClip] Descending.")

if __name__ == "__main__":
    vox = VoxClip()
    vox.run()
