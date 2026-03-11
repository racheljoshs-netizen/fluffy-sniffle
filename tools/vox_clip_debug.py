"""
VoxClip v1.1 - DEBUG VERSION
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

# CUDA Setup
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

class VoxClip:
    def __init__(self):
        print("[VoxClip] Initializing Engine...")
        model_path = AGENCY_DIR / "kokoro-v1.0.onnx"
        voice_path = AGENCY_DIR / "voices-v1.0.bin"
        
        print(f"[DEBUG] Model: {model_path} (Exists: {model_path.exists()})")
        print(f"[DEBUG] Voice: {voice_path} (Exists: {voice_path.exists()})")
        
        try:
            self.kokoro = Kokoro(str(model_path), str(voice_path))
            print("[DEBUG] Kokoro loaded successfully.")
        except Exception as e:
            print(f"[CRITICAL] Kokoro Init Failed: {e}")
            sys.exit(1)

        self.text_queue = queue.Queue()
        self.is_paused = False
        self.is_running = True
        
        keyboard.add_hotkey('ctrl+shift+space', self.toggle_pause)
        keyboard.add_hotkey('ctrl+shift+x', self.stop_speech)
        
        print("[VoxClip] Online. Monitoring Clipboard.")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        print(f"[VoxClip] {'PAUSED' if self.is_paused else 'RESUMED'}")
        if self.is_paused: sd.stop()

    def stop_speech(self):
        print("[VoxClip] STOPPING.")
        while not self.text_queue.empty(): self.text_queue.get_nowait()
        sd.stop()

    def speak_worker(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
            try:
                text = self.text_queue.get(timeout=0.5)
                print(f"[DEBUG] Processing: {text[:30]}...")
                sentences = text.replace("\n", ". ").split(". ")
                for sentence in sentences:
                    if not self.is_running or self.is_paused or not sentence.strip(): continue
                    
                    print(f"[DEBUG] Generating audio for: {sentence[:30]}...")
                    samples, sample_rate = self.kokoro.create(sentence, voice="am_adam", speed=1.1, lang="en-us")
                    
                    print(f"[DEBUG] Playing audio ({len(samples)} samples)...")
                    sd.play(samples, sample_rate)
                    sd.wait() # Use synchronous wait for debug version
                    print("[DEBUG] Playback finished.")
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoxClip] Speech Error: {e}")

    def monitor_clipboard(self):
        print("[DEBUG] Clipboard monitor started.")
        last_clip = pyperclip.paste()
        while self.is_running:
            try:
                current_clip = pyperclip.paste()
                if current_clip != last_clip:
                    print(f"[DEBUG] Clipboard change detected: {current_clip[:20]}")
                    if current_clip.strip():
                        self.text_queue.put(current_clip)
                    last_clip = current_clip
                time.sleep(0.5)
            except Exception as e:
                print(f"[VoxClip] Clipboard Error: {e}")
                time.sleep(1)

    def run(self):
        t = threading.Thread(target=self.speak_worker, daemon=True)
        t.start()
        self.monitor_clipboard()

if __name__ == "__main__":
    vox = VoxClip()
    vox.run()
