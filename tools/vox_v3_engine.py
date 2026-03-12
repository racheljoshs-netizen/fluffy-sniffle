import os
import time
import asyncio
import threading
import edge_tts
import pygame
import keyboard
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- VOX V3: THE SIGNAL WATCHER ---
# High-fidelity, File-triggered TTS Pipeline.
# Does not rely on the clipboard. Bypasses flaky OS buffers.

SIGNAL_FILE = Path("E:/0x/vox_tmp/signal.txt")
TMP_DIR = Path("E:/0x/vox_tmp")
VOICE = "en-US-AndrewNeural"
DEVICE = "Headphones (2- VIPEX VX-SK001)"

TMP_DIR.mkdir(exist_ok=True)
if not SIGNAL_FILE.exists():
    SIGNAL_FILE.write_text("", encoding="utf-8")

class VoxV3Handler(FileSystemEventHandler):
    def __init__(self, engine):
        self.engine = engine

    def on_modified(self, event):
        if Path(event.src_path).resolve() == SIGNAL_FILE.resolve():
            text = SIGNAL_FILE.read_text(encoding="utf-8").strip()
            if text:
                print(f"\n[VOX V3] SIGNAL DETECTED: {text[:50]}...")
                self.engine.add_to_queue(text)
                # Clear signal file to avoid re-triggering on same content
                SIGNAL_FILE.write_text("", encoding="utf-8")

class VoxEngine:
    def __init__(self):
        print("[VOX V3] INITIALIZING ENGINE...")
        try:
            pygame.mixer.init(devicename=DEVICE)
            print(f"[VOX V3] ROUTED TO: {DEVICE}")
        except:
            pygame.mixer.init()
            print("[VOX V3] ROUTED TO DEFAULT AUDIO.")

        self.queue = asyncio.Queue()
        self.is_paused = False
        self.is_running = True
        self.file_counter = 0

        # Global Hotkeys
        keyboard.add_hotkey('ctrl+shift+space', self.toggle_pause)
        keyboard.add_hotkey('ctrl+shift+x', self.purge)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        print(f"[VOX V3] {'PAUSED' if self.is_paused else 'RESUMED'}")
        if self.is_paused: pygame.mixer.music.pause()
        else: pygame.mixer.music.unpause()

    def purge(self):
        print("[VOX V3] TACTICAL PURGE.")
        while not self.queue.empty():
            self.queue.get_nowait()
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def add_to_queue(self, text):
        # We use a separate thread loop for the async worker
        self.loop.call_soon_threadsafe(self.queue.put_nowait, text)

    async def _play(self, text):
        self.file_counter += 1
        fname = TMP_DIR / f"v3_{self.file_counter % 20}.mp3"
        
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
            print(f"[ERROR] Playback failed: {e}")

    async def worker(self):
        while self.is_running:
            text = await self.queue.get()
            # Chunking for fluid control
            chunks = [s.strip() for s in text.replace("\n", ". ").split(". ") if s.strip()]
            for chunk in chunks:
                if not self.is_running: break
                await self._play(chunk)
            self.queue.task_done()

    def run(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_until_complete, args=(self.worker(),), daemon=True).start()
        
        # Start Watchdog
        observer = Observer()
        observer.schedule(VoxV3Handler(self), str(TMP_DIR), recursive=False)
        observer.start()
        
        print("[VOX V3] MONITORING SIGNAL FILE. STANDING BY.")
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            self.is_running = False
            observer.stop()
        observer.join()

if __name__ == "__main__":
    engine = VoxEngine()
    engine.run()
