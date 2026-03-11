# G. Opportunity Voice Terminal

Push-to-talk voice interface to Clawdbot.

## Setup

1. Run `install.bat` (one-time)
2. Run `run.bat` to start

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Hold to talk (push-to-talk) |
| **M** | Toggle always-listen mode |
| **ESC** | Quit |

## How it works

1. Hold SPACE and speak
2. Release SPACE — Whisper transcribes locally
3. Text sent to Clawdbot gateway
4. Response played back via ElevenLabs TTS

## Config

Edit `voice_terminal.py` to change:
- `WHISPER_MODEL` — tiny/base/small/medium/large (bigger = better but slower)
- `ELEVENLABS_VOICE_ID` — Different voice
- `GATEWAY_URL` — If gateway runs elsewhere

## Requirements

- Python 3.10+
- Microphone
- Speakers/headphones
- Clawdbot gateway running locally

## Troubleshooting

**No audio captured:** Check microphone permissions and default device.

**Slow transcription:** Use `tiny` model instead of `base`.

**Gateway connection failed:** Ensure Clawdbot gateway is running (`clawdbot gateway status`).
