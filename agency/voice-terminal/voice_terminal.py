#!/usr/bin/env python3
"""
G. Voice Assistant — Always-on, fully local.
STT: Whisper (GPU) | LLM: Ollama | TTS: pyttsx3
No push-to-talk. VAD auto-detects speech. Just talk.
"""

import os
import sys
import time
import wave
import tempfile
import threading
import queue
import numpy as np
import sounddevice as sd
import whisper
import pyttsx3
import requests
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout

# ============================================================================
# CONFIG
# ============================================================================

OPENROUTER_KEY = "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"
OPENROUTER_MODEL = "google/gemini-2.0-flash-001"

SAMPLE_RATE = 16000
CHANNELS = 1
WHISPER_MODEL = "base"

# VAD settings
VAD_ENERGY_THRESHOLD = 0.012   # mic energy above this = speech
SILENCE_TIMEOUT = 1.8          # seconds of silence after speech to trigger processing
MIN_SPEECH_DURATION = 0.4      # minimum seconds of speech to process

# System context
ROOT_DIR = Path(__file__).parent.parent
SYSTEM_PROMPT_PATH = ROOT_DIR / "instructions.md"
MEMORY_PATH = ROOT_DIR / "MEMORY_V2.md"

console = Console()

# ============================================================================
# STATE
# ============================================================================

class AssistantState:
    status = "BOOTING"
    energy = 0.0
    last_user = ""
    last_response = ""
    orb_tick = 0
    speaking = False

state = AssistantState()

# ============================================================================
# SYSTEM CONTEXT
# ============================================================================

_cached_context = None

def get_system_context():
    global _cached_context
    if _cached_context is None:
        context = ""
        if SYSTEM_PROMPT_PATH.exists():
            context += SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        if MEMORY_PATH.exists():
            context += "\n\n### OPERATIONAL MEMORY:\n"
            context += MEMORY_PATH.read_text(encoding="utf-8")
        # Keep it under 2k tokens to avoid Ollama timeouts
        if len(context) > 4000:
            context = context[:4000]
        _cached_context = context
    return _cached_context

# ============================================================================
# TTS (local)
# ============================================================================

tts_engine = None
tts_lock = threading.Lock()

def init_tts():
    global tts_engine
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 175)
    voices = tts_engine.getProperty('voices')
    for v in voices:
        if 'zira' in v.name.lower() or 'female' in v.name.lower():
            tts_engine.setProperty('voice', v.id)
            break

def speak(text: str):
    if not text or not text.strip():
        return
    # Strip markdown headers/formatting for cleaner speech
    clean = text.replace('#', '').replace('*', '').replace('`', '').strip()
    # Truncate very long responses for speech
    if len(clean) > 800:
        clean = clean[:800] + "... I'll stop there."
    state.speaking = True
    state.status = "SPEAKING"
    try:
        with tts_lock:
            tts_engine.say(clean)
            tts_engine.runAndWait()
    except Exception as e:
        pass
    state.speaking = False
    state.status = "LISTENING"

# ============================================================================
# LLM (OpenRouter — fast cloud model, voice stays local)
# ============================================================================

conversation_history = []

def send_to_llm(message: str) -> str:
    state.status = "THINKING"
    system_context = get_system_context()

    conversation_history.append({"role": "user", "content": message})
    if len(conversation_history) > 12:
        conversation_history[:] = conversation_history[-12:]

    messages = [{"role": "system", "content": system_context}] + conversation_history

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": messages,
                "max_tokens": 300,
            },
            timeout=30
        )
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            conversation_history.append({"role": "assistant", "content": reply})
            return reply
        return f"API error {response.status_code}"
    except requests.Timeout:
        return "Timed out."
    except Exception as e:
        return f"Error: {e}"

# ============================================================================
# ORB VISUALIZATION
# ============================================================================

def render_orb():
    state.orb_tick += 1
    e = min(state.energy * 80, 10)

    status_colors = {
        "BOOTING": "yellow",
        "LISTENING": "green",
        "RECORDING": "red",
        "THINKING": "magenta",
        "SPEAKING": "cyan",
    }
    color = status_colors.get(state.status, "white")

    # Animated orb
    base = 3
    size = base + int(e)
    if state.status == "SPEAKING":
        size = base + (state.orb_tick % 3)
    if size > 10:
        size = 10

    lines = []
    for i in range(size):
        dist = abs(i - size // 2)
        width = (size - dist) * 2
        char = "o" if state.status == "SPEAKING" else "."
        line = f"[bold {color}]{char * width}[/]"
        lines.append(f"{'':>{20 - width // 2}}{line}")

    orb_str = "\n".join(lines) if lines else f"[{color}]...[/]"
    return orb_str

def render_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="orb", size=14),
        Layout(name="log", size=8),
    )

    status_txt = f"[bold cyan]NAVIGATOR G[/]  |  [{('green' if state.status=='LISTENING' else 'yellow')}]{state.status}[/]  |  Voice: Local  |  LLM: Cloud"
    layout["header"].update(Panel(status_txt, style="blue"))
    layout["orb"].update(Panel(Align.center(render_orb()), title="[bold]Voice Activity[/]", border_style="cyan"))

    user_line = f"[dim]You:[/] {state.last_user[-120:]}" if state.last_user else "[dim]You:[/] ..."
    resp_line = f"[dim]G:[/] {state.last_response[-200:]}" if state.last_response else "[dim]G:[/] ..."
    layout["log"].update(Panel(f"{user_line}\n{resp_line}", title="Conversation", border_style="dim"))

    return layout

# ============================================================================
# VOICE CAPTURE (always-on VAD)
# ============================================================================

audio_buffer = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    energy = np.linalg.norm(indata) / np.sqrt(len(indata))
    state.energy = energy
    audio_buffer.put((indata.copy(), energy))

def capture_speech(whisper_model):
    """Block until speech is detected, capture it, return transcription."""
    frames = []
    speech_started = False
    silence_start = None
    speech_duration = 0.0
    frame_duration = 1024 / SAMPLE_RATE  # ~0.064s per frame

    while True:
        try:
            data, energy = audio_buffer.get(timeout=0.2)
        except queue.Empty:
            continue

        if state.speaking:
            # Don't capture while TTS is playing (echo suppression)
            continue

        if energy > VAD_ENERGY_THRESHOLD:
            if not speech_started:
                speech_started = True
                state.status = "RECORDING"
                frames = frames[-10:]  # keep small pre-buffer
            frames.append(data)
            speech_duration += frame_duration
            silence_start = None
        else:
            if speech_started:
                frames.append(data)
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_TIMEOUT:
                    break
            else:
                # Pre-buffer a bit
                frames.append(data)
                if len(frames) > 15:
                    frames = frames[-15:]

    if speech_duration < MIN_SPEECH_DURATION:
        state.status = "LISTENING"
        return None

    # Transcribe
    state.status = "THINKING"
    audio_data = np.concatenate(frames, axis=0)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name

    with wave.open(temp_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

    try:
        result = whisper_model.transcribe(temp_path, language="en", fp16=False)
        text = result["text"].strip()
    except Exception:
        text = ""
    finally:
        os.unlink(temp_path)

    return text if text else None

# ============================================================================
# MAIN LOOP
# ============================================================================

def assistant_loop(whisper_model):
    """Runs in a thread. Listens -> transcribes -> thinks -> speaks. Repeat."""
    state.status = "LISTENING"

    while True:
        text = capture_speech(whisper_model)
        if not text:
            state.status = "LISTENING"
            continue

        state.last_user = text
        response = send_to_llm(text)
        state.last_response = response
        speak(response)
        state.status = "LISTENING"

def main():
    console.print("[bold cyan]NAVIGATOR G — Voice Assistant[/]")
    console.print("[dim]Fully local. Always listening. Just talk.[/]\n")

    # Init TTS
    console.print("[yellow]Initializing TTS...[/]")
    init_tts()

    # Load Whisper
    console.print("[yellow]Loading Whisper model...[/]")
    whisper_model = whisper.load_model(WHISPER_MODEL)

    # Start mic
    console.print("[yellow]Starting microphone...[/]")
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32',
        callback=audio_callback,
        blocksize=1024
    )
    stream.start()

    # Announce ready
    state.status = "LISTENING"
    speak("Online. Listening.")

    # Start assistant loop in background thread
    t = threading.Thread(target=assistant_loop, args=(whisper_model,), daemon=True)
    t.start()

    # Render orb UI
    try:
        with Live(render_layout(), refresh_per_second=8, console=console) as live:
            while True:
                live.update(render_layout())
                time.sleep(0.125)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        stream.close()
        console.print("\n[dim]Goodbye.[/]")

if __name__ == "__main__":
    main()
