# G-Pattern Sovereign Identity Engine — Architecture

## Current State: Production-Ready (v1.0)

All four components implemented and clean. No duplicate modules. No stubs.

## File Manifest

| File | Role | Status |
|---|---|---|
| `proxy.py` | FastAPI proxy — request pipeline, injection, streaming, post-process | Complete |
| `librarian.py` | Librarian class — card retrieval, audit gating, extraction, upserts, consolidation | Complete |
| `config.yaml` | All configurable params — models, paths, thresholds, consolidation rates | Complete |
| `schema.sql` | SQLite DDL — `heuristic_cards` + indexes + `consolidation_logs` | Complete |
| `directives.txt` | Full OPERATIONAL DIRECTIVES — injected verbatim into every main-model prompt | Complete |
| `requirements.txt` | Pinned Python deps | Complete |
| `start.bat` | One-command launch — Ollama + model pull + proxy | Complete |

## Architecture (Component 1 Invariants)

```
Frontend (Open WebUI / curl / anything)
    │
    ▼  POST /v1/chat/completions (OpenAI-compatible)
┌──────────────────────────────────────┐
│           proxy.py (FastAPI)         │
│                                      │
│  1. Extract tail (last ~6 messages)  │
│  2. Librarian.get_relevant_cards()   │
│     → SQLite query + embedding sim   │
│  3. Check for [SYS_CALL: AUDIT]     │
│     → Librarian gatekeeper           │
│  4. Build augmented system prompt    │
│     [DIRECTIVES + CARDS + LOGS]      │
│  5. litellm.acompletion() → backend  │
│  6. Stream SSE back to frontend      │
│  7. Async post_process_turn()        │
│     → Chroma insert + Gemma extract  │
│     → SQLite upserts (full merge)    │
└──────────────────────────────────────┘
    │                    │
    ▼                    ▼
Main Model API      Librarian (Gemma 3n:4b via Ollama)
(invisible to       + BGE-small-en (embedding)
 librarian)         + SQLite (Heuristic Rolodex)
                    + ChromaDB (Verbatim Vault)
```

## Invariant Compliance

- Main model sees only native context window ✓
- No artificial chunking or forced markers ✓
- Librarian invisible to main model ✓
- Two databases only (SQLite + ChromaDB) ✓
- Cards mutable, raw logs immutable (sacred) ✓
- Audit access deliberately expensive ✓
- Fits in 12GB VRAM (3060) ✓
- Frontend is dumb terminal ✓

## Launch

```bat
cd e:\0x\sovereign_identity
start.bat
```

Or manually:

```powershell
ollama serve
ollama pull gemma3n:4b
python proxy.py
```

Then point any OpenAI-compatible client at `http://localhost:8000/v1/chat/completions`.
