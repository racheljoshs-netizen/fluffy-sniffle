import asyncio
import os
import time
import threading
import queue
import pyperclip
import keyboard
import edge_tts
import pygame
from pathlib import Path

# --- G-PRIME VOX CASTER V2 ---
# Clipboard-to-TTS Pipeline with Instant Kinetic Control

VOICE = "en-US-AndrewNeural"
TMP_DIR = Path("E:/0x/vox_tmp")
TMP_DIR.mkdir(exist_ok=True)

class VoxCaster:
    def __init__(self):
        print("[VOX CASTER V2] INITIALIZING SENSORY INTERFACE...")
        try:
            pygame.mixer.init(devicename="Headphones (2- VIPEX VX-SK001)")
            print("[VOX] ROUTED TO: Headphones (2- VIPEX VX-SK001)")
        except Exception as e:
            print(f"[WARN] Failed to route, using default. {e}")
            pygame.mixer.init()
        
        self.text_queue = queue.Queue()
        self.is_paused = False
        self.is_running = True
        self.current_file = None
        self.file_counter = 0
        
        # Kinetic Hotkeys
        keyboard.add_hotkey('ctrl+shift+space', self.toggle_pause)
        keyboard.add_hotkey('ctrl+shift+x', self.purge_queue)
        
        print("[VOX CASTER V2] LOCKED ON. MONITORING CLIPBOARD [CTRL+SHIFT+SPACE: Pause | CTRL+SHIFT+X: Purge]")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        state = "PAUSED" if self.is_paused else "RESUMED"
        print(f"[VOX] PLAYBACK {state}.")
        if self.is_paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def purge_queue(self):
        print("[VOX] TACTICAL PURGE INITIATED. CLEARING QUEUE.")
        while not self.text_queue.empty():
            try: self.text_queue.get_nowait()
            except: break
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    async def _synthesize_and_play(self, text):
        if not text.strip(): return
        
        self.file_counter += 1
        fname = TMP_DIR / f"caster_{self.file_counter % 20}.mp3"
        
        communicate = edge_tts.Communicate(text, VOICE, rate="+10%")
        await communicate.save(str(fname))
        
        try:
            pygame.mixer.music.load(str(fname))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy() or self.is_paused:
                if not self.is_running: break
                await asyncio.sleep(0.1)
                
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"[ERROR] VOX FAILURE: {e}")

    def audio_worker(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.is_running:
            try:
                # Wait for text payload
                text = self.text_queue.get(timeout=0.5)
                
                # Chunking large blocks into sentences for fluid pause/purge
                chunks = [s.strip() for s in text.replace("\n", ". ").split(". ") if s.strip()]
                
                for chunk in chunks:
                    if not self.is_running: break
                    print(f"[VOX] INJECTING: {chunk[:60]}...")
                    loop.run_until_complete(self._synthesize_and_play(chunk))
                    
            except queue.Empty:
                continue

    def monitor_clipboard(self):
        last_clip = pyperclip.paste()
        while self.is_running:
            try:
                current_clip = pyperclip.paste()
                if current_clip != last_clip and current_clip.strip():
                    print(f"\n[VOX] PAYLOAD DETECTED. LENGTH: {len(current_clip)} CHARS.")
                    self.text_queue.put(current_clip)
                    last_clip = current_clip
                time.sleep(0.2)
            except Exception as e:
                time.sleep(1)

    def ignite(self):
        t = threading.Thread(target=self.audio_worker, daemon=True)
        t.start()
        try:
            self.monitor_clipboard()
        except KeyboardInterrupt:
            self.is_running = False
            print("\n[VOX CASTER V2] GOING DARK.")

if __name__ == "__main__":
    caster = VoxCaster()
    caster.ignite()
