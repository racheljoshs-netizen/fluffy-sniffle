import asyncio
import edge_tts
import pygame
import os

VOICE = "en-US-AndrewNeural"
OUTPUT_FILE = "E:/0x/diag_test.mp3"
TEXT = "Diagnostics active. Checking audio substrate."

async def diag():
    print(f"[Diag] Synthesizing: {TEXT}")
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    
    print("[Diag] Initializing Mixer...")
    pygame.mixer.init()
    
    print("[Diag] Loading and Playing...")
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
    print("[Diag] Done.")

if __name__ == "__main__":
    asyncio.run(diag())
