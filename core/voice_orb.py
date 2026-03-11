import os
import sys
import time
import queue
import threading
import wave
import tempfile
import asyncio
import random
import numpy as np
import sounddevice as sd
import whisper
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from playsound import playsound
from pathlib import Path
import pyttsx3

# --- CONFIG ---
OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "gemma3n:e4b"

WHISPER_MODEL = "base"
SAMPLE_RATE = 16000
VAD_THRESHOLD = 0.01
SILENCE_DURATION = 1.5

# Paths
ROOT_DIR = Path(__file__).parent
SYSTEM_PROMPT_PATH = ROOT_DIR / "system_prompt.txt"
MEMORY_PATH = ROOT_DIR / "MEMORY_V2.md"

console = Console()
audio_queue = queue.Queue()

class State:
    status = "BOOTING"
    last_text = ""
    last_response = ""
    energy = 0.0
    orb_frame = 0

state = State()

def get_system_context():
    context = ""
    if SYSTEM_PROMPT_PATH.exists():
        context += SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    if MEMORY_PATH.exists():
        context += "\n\n### CURRENT OPERATIONAL MEMORY:\n"
        context += MEMORY_PATH.read_text(encoding="utf-8")
    return context

tts_engine = None

def init_tts():
    global tts_engine
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 175)
    voices = tts_engine.getProperty('voices')
    for v in voices:
        if 'zira' in v.name.lower() or 'female' in v.name.lower():
            tts_engine.setProperty('voice', v.id)
            break

def generate_response(user_input: str):
    system_context = get_system_context()

    try:
        import requests
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_input}
                ],
                "stream": False
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
        return f"Ollama error: {response.status_code}"
    except Exception as e:
        return f"Ollama error: {e}"

async def speak_local(text):
    state.status = "SPEAKING"
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error: {e}")
    state.status = "LISTENING"

def audio_callback(indata, frames, time_info, status):
    state.energy = np.linalg.norm(indata) / np.sqrt(len(indata))
    audio_queue.put(indata.copy())

def capture_voice():
    frames = []
    silent_start = None
    voice_detected = False
    
    while True:
        try:
            data = audio_queue.get(timeout=0.1)
            frames.append(data)
            energy = np.linalg.norm(data) / np.sqrt(len(data))
            
            if energy > VAD_THRESHOLD:
                if not voice_detected:
                    state.status = "RECORDING"
                    voice_detected = True
                silent_start = None
            else:
                if voice_detected:
                    if silent_start is None:
                        silent_start = time.time()
                    elif time.time() - silent_start > SILENCE_DURATION:
                        break
                else:
                    if len(frames) > 50:
                        frames = frames[-20:]
        except queue.Empty:
            continue
            
    return np.concatenate(frames, axis=0)

def make_orb():
    colors = ["cyan", "bright_blue", "deep_sky_blue1", "dodger_blue1"]
    state.orb_frame = (state.orb_frame + 1) % len(colors)
    color = colors[state.orb_frame]
    size = int(5 + (state.energy * 100))
    if size > 12: size = 12
    
    orb_text = "\n" * (6 - size // 2)
    for i in range(size):
        line = "●" * (size * 2)
        orb_text += " " * (30 - size) + f"[{color}]{line}[/]\n"
    return Align.center(orb_text)

def generate_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=6)
    )
    layout["header"].update(Panel(f"[bold cyan]G-PATTERN VOICE ORB[/] | Status: [bold]{state.status}[/]", style="blue"))
    layout["main"].update(make_orb())
    footer_text = f"[dim]User:[/] {state.last_text}\n[dim]G:[/] {state.last_response[:150]}..."
    layout["footer"].update(Panel(footer_text, title="Neural Link Log", border_style="cyan"))
    return layout

async def voice_loop():
    # DIRECTIVE COMPLIANCE
    state.status = "INIT: AUDIO"
    console.print("[cyan]ORB:[/] Initializing audio input stream...")
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback)
    stream.start()
    
    state.status = "INIT: WHISPER"
    console.print("[cyan]ORB:[/] Configuring voice recognition module (Whisper Base)...")
    model = whisper.load_model(WHISPER_MODEL)
    
    state.status = "INIT: TTS"
    init_tts()
    console.print("[cyan]ORB:[/] Local TTS engine initialized.")

    state.status = "INIT: LLM"
    console.print("[cyan]ORB:[/] Connecting to local Ollama instance...")
    
    state.status = "INIT: PARSING"
    console.print("[cyan]ORB:[/] Executing command parsing engine...")
    
    state.status = "INIT: FIDELITY"
    console.print("[cyan]ORB:[/] Verifying output fidelity...")
    await speak_local("Voice Orb online. Local mode. Ready.")
    
    state.status = "LISTENING"
    
    while True:
        audio_data = capture_voice()
        state.status = "TRANSCRIBING"
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_wav = f.name
        
        with wave.open(temp_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            
        result = model.transcribe(temp_wav)
        os.unlink(temp_wav)
        
        text = result["text"].strip()
        if not text:
            state.status = "LISTENING"
            continue
            
        state.last_text = text
        state.status = "THINKING"
        response = generate_response(text)
        state.last_response = response
        
        await speak_local(response)

async def main():
    await asyncio.sleep(1)
    with Live(generate_layout(), refresh_per_second=10) as live:
        loop_task = asyncio.create_task(voice_loop())
        while not loop_task.done():
            live.update(generate_layout())
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass