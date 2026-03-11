"""
VoxEdge v1.3 - Permission Denied Fix
Uses rotating files to avoid lock contention.
"""

import asyncio
import os
import sys
import time
import threading
import queue
import pyperclip
import keyboard
import edge_tts
import pygame
from pathlib import Path

VOICE = "en-US-AndrewNeural"
DEVICE_NAME = "Headphones (2- VIPEX VX-SK001)"
TMP_DIR = Path("E:/0x/vox_tmp")
TMP_DIR.mkdir(exist_ok=True)

class VoxEdge:
    def __init__(self):
        print("[VoxEdge] Initializing Interface...")
        try:
            pygame.mixer.init(devicename=DEVICE_NAME)
            print(f"[VoxEdge] Routed to: {DEVICE_NAME}")
        except Exception as e:
            print(f"[Warning] Failed to route, using default. {e}")
            pygame.mixer.init()
            
        self.text_queue = queue.Queue()
        self.is_paused = False
        self.is_running = True
        self.loop = asyncio.new_event_loop()
        self.file_counter = 0
        
        keyboard.add_hotkey('ctrl+shift+space', self.toggle_pause)
        keyboard.add_hotkey('ctrl+shift+x', self.stop_speech)
        
        print(f"[VoxEdge] Online. Monitoring Clipboard.")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        print(f"[VoxEdge] {'PAUSED' if self.is_paused else 'RESUMED'}")
        if self.is_paused: pygame.mixer.music.pause()
        else: pygame.mixer.music.unpause()

    def stop_speech(self):
        print("[VoxEdge] STOPPING.")
        while not self.text_queue.empty():
            try: self.text_queue.get_nowait()
            except: break
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    async def _generate_and_play(self, text):
        if not text.strip(): return
        
        # Use a unique filename for every call to avoid locks
        self.file_counter += 1
        fname = TMP_DIR / f"speech_{self.file_counter % 10}.mp3" # Cycle 10 files
        
        print(f"[VoxEdge] Synthesizing: {text[:50]}...")
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(fname))
        
        print("[VoxEdge] Playing...")
        try:
            pygame.mixer.music.load(str(fname))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                if not self.is_running or self.is_paused:
                    break
                await asyncio.sleep(0.1)
            
            pygame.mixer.music.unload() # Crucial to release the file
        except Exception as e:
            print(f"[VoxEdge] Playback Error: {e}")

    def speak_worker(self):
        asyncio.set_event_loop(self.loop)
        while self.is_running:
            try:
                text = self.text_queue.get(timeout=0.5)
                # Split by sentence for smoother interruptions
                sentences = text.replace("\n", ". ").split(". ")
                for s in sentences:
                    if not self.is_running or self.is_paused or not s.strip(): continue
                    self.loop.run_until_complete(self._generate_and_play(s))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoxEdge] Worker Error: {e}")

    def monitor_clipboard(self):
        last_clip = pyperclip.paste()
        while self.is_running:
            try:
                current_clip = pyperclip.paste()
                if current_clip != last_clip:
                    if current_clip.strip():
                        print(f"[VoxEdge] New clipboard detected.")
                        self.text_queue.put(current_clip)
                    last_clip = current_clip
                time.sleep(0.5)
            except Exception as e:
                print(f"[VoxEdge] Clipboard Error: {e}")
                time.sleep(1)

    def run(self):
        t = threading.Thread(target=self.speak_worker, daemon=True)
        t.start()
        try:
            self.monitor_clipboard()
        except KeyboardInterrupt:
            self.is_running = False
            print("[VoxEdge] Descending.")

if __name__ == "__main__":
    vox = VoxEdge()
    vox.run()
